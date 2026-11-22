"""Run the OTA regression suite against a local HTTP server and virtual flash."""

import argparse
import csv
import http.server
import json
from pathlib import Path
import queue
import select
import socket
import subprocess
import threading
import time

CASES = {
    "baseline",
    "boot_error",
    "allocation_error",
    "http_404",
    "http_500",
    "stall_timeout",
}
TIMEOUT_S = 150
PANIC_LOG_TIMEOUT_S = 2


def results_from(output):
    results = {}
    for line in output.splitlines():
        if line.startswith("CASE_RESULT "):
            _, name, status, *_ = line.split()
            if name not in CASES or name in results or status not in {"PASS", "FAIL"}:
                raise ValueError(f"Invalid or duplicate result: {line}")
            results[name] = status
    if "SUITE_DONE" not in output.splitlines() or set(results) != CASES:
        raise ValueError("Suite did not finish with all six results")
    return results


def expected_failures(expect_buggy, expect_fail):
    unknown = set(expect_fail) - CASES
    if unknown:
        raise ValueError(f"Unknown test cases in --expect-fail: {sorted(unknown)}")
    if expect_buggy:
        return CASES - {"baseline"}
    return set(expect_fail)


def write_csv(output, path):
    """Save every CASE_RESULT line as one CSV row."""
    rows = []
    for line in output.splitlines():
        if line.startswith("CASE_RESULT "):
            _, name, status, *fields = line.split()
            row = {"case": name, "result": status}
            row.update(field.split("=", 1) for field in fields if "=" in field)
            rows.append(row)
    columns = ["case", "result"]
    for row in rows:
        columns += [key for key in row if key not in columns]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--qemu", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--log", type=Path)
    mode.add_argument("--shell", action="store_true", help="attach the terminal to the guest UART")
    parser.add_argument("--csv", type=Path, help="save the case results to this CSV file")
    parser.add_argument("--expect-buggy", action="store_true",
                        help="require the baseline to pass and all five regression cases to fail")
    parser.add_argument("--expect-fail", action="append", default=[],
                        help="name a test case expected to fail")
    args = parser.parse_args()
    build = args.build.resolve()
    image = bytearray(b"\xff" * (4 * 1024 * 1024))
    flash_args = json.loads((build / "flasher_args.json").read_text())
    for offset, filename in flash_args["flash_files"].items():
        data = (build / filename).read_bytes()
        start = int(offset, 0)
        if start + len(data) > len(image):
            raise ValueError("Firmware exceeds virtual flash size")
        image[start : start + len(data)] = data
    flash = build / "qemu-flash.bin"
    firmware = (build / "ota_repro.bin").read_bytes()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/stall":
                self.send_response(200)
                self.send_header("Content-Length", str(len(firmware)))
                self.end_headers()
                try:
                    self.wfile.write(firmware[:2048])
                    self.wfile.flush()
                    end = time.monotonic() + 8.0
                    while time.monotonic() < end:
                        readable, _, _ = select.select([self.connection], [], [], 0.2)
                        if readable:
                            if not self.connection.recv(1, socket.MSG_PEEK):
                                break
                except OSError:
                    pass
                return
            if self.path == "/image.bin":
                status, body = 200, firmware
            elif self.path == "/500":
                status, body = 500, b"test server error"
            else:
                status, body = 404, b"test file not found"
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 18080), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    command = [str(args.qemu.resolve()), "-display", "none", "-serial", "stdio", "-monitor", "none",
               "-machine", "esp32", "-global", "driver=timer.esp32.timg,property=wdt_disable,value=true",
               "-drive", f"file={flash},if=mtd,format=raw",
               "-nic", "user,model=open_eth"]
    log = None
    try:
        flash.write_bytes(image)
        if args.shell:
            try:
                return subprocess.run(command, check=False).returncode
            except KeyboardInterrupt:
                return 130
        lines = []
        stop_reason = None
        messages = queue.Queue()
        args.log.parent.mkdir(parents=True, exist_ok=True)
        log = args.log.open("w")
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                                   text=True, errors="replace")

        def read_output():
            for line in process.stdout:
                messages.put(line)
            messages.put(None)

        threading.Thread(target=read_output, daemon=True).start()
        try:
            deadline = time.monotonic() + TIMEOUT_S
            while time.monotonic() < deadline:
                try:
                    line = messages.get(timeout=min(1, max(0.01, deadline - time.monotonic())))
                except queue.Empty:
                    continue
                if line is None:
                    stop_reason = stop_reason or "QEMU exited before SUITE_DONE"
                    break
                log.write(line)
                log.flush()
                if stop_reason is not None:
                    continue
                lines.append(line)
                if line.startswith(("CASE_", "SUITE_DONE")):
                    print(line.rstrip(), flush=True)
                if line.strip() == "SUITE_DONE":
                    break
                if "Guru Meditation Error" in line:
                    stop_reason = "the guest crashed (Guru Meditation Error)"
                    deadline = time.monotonic() + PANIC_LOG_TIMEOUT_S
            else:
                stop_reason = stop_reason or f"no SUITE_DONE within {TIMEOUT_S} seconds"
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    finally:
        server.shutdown()
        server.server_close()
        if log is not None:
            log.close()
    output = "".join(lines)
    if args.csv:
        write_csv(output, args.csv)
    try:
        results = results_from(output)
    except ValueError as error:
        if stop_reason:
            print(f"Suite failed: {stop_reason}. {error} See {args.log}.")
        else:
            print(f"Suite failed: {error} See {args.log}.")
        return 1
    failed = {name for name, result in results.items() if result == "FAIL"}
    expected = expected_failures(args.expect_buggy, args.expect_fail)
    if failed != expected:
        print(f"Expected failing cases: {sorted(expected)}. Observed: {sorted(failed)}.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
