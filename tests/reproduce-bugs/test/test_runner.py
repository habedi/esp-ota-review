from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from run_qemu import CASES, expected_failures, main, results_from


class ResultTests(unittest.TestCase):
    def test_crash_or_missing_case_cannot_pass(self):
        with self.assertRaises(ValueError):
            results_from("CASE_RESULT baseline PASS\nSUITE_DONE\n")
        with self.assertRaises(ValueError):
            results_from("".join(f"CASE_RESULT {name} PASS\n" for name in CASES))

    def test_failed_regression_is_preserved(self):
        output = "".join(f"CASE_RESULT {name} {'FAIL' if name == 'boot_error' else 'PASS'}\n"
                         for name in CASES) + "SUITE_DONE\n"
        self.assertEqual(results_from(output)["boot_error"], "FAIL")
        with self.assertRaises(ValueError):
            results_from(output + "CASE_RESULT baseline PASS\n")

    def test_expected_failures_validation(self):
        self.assertEqual(expected_failures(True, []), CASES - {"baseline"})
        self.assertEqual(expected_failures(False, ["stall_timeout"]), {"stall_timeout"})
        self.assertEqual(expected_failures(False, []), set())
        with self.assertRaises(ValueError):
            expected_failures(False, ["unknown_case"])


class ConsoleTests(unittest.TestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.build = Path(stack.enter_context(TemporaryDirectory()))
        (self.build / "flasher_args.json").write_text('{"flash_files": {}}')
        (self.build / "ota_repro.bin").write_bytes(b"")
        argv = ["run_qemu.py", str(self.build), "--qemu", "qemu", "--shell"]
        stack.enter_context(patch("sys.argv", argv))
        self.server = stack.enter_context(patch("run_qemu.http.server.ThreadingHTTPServer"))

    def test_console_uses_the_terminal_without_a_log(self):
        with patch("run_qemu.subprocess.run") as qemu:
            qemu.return_value.returncode = 0
            self.assertEqual(main(), 0)
            self.assertEqual(qemu.call_args.kwargs, {"check": False})
            self.server.return_value.shutdown.assert_called_once()

    def test_busy_port_leaves_virtual_flash_alone(self):
        flash = self.build / "qemu-flash.bin"
        flash.write_bytes(b"active guest flash")
        self.server.side_effect = OSError("address already in use")
        with self.assertRaises(OSError):
            main()
        self.assertEqual(flash.read_bytes(), b"active guest flash")


if __name__ == "__main__":
    unittest.main()
