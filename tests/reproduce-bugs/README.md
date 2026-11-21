## Bug Reproduction

This directory contains test cases for reproducing bugs that we found during
reviewing [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c).

### What Is Tested

[main/main.c](main/main.c) runs six cases in ESP32 QEMU against a local HTTP server ([test/run_qemu.py](test/run_qemu.py)).
It compares the pinned review SDK (`7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00`), an optional generated `fixed` copy in `build/`, and ESP-IDF `v6.1.1`:

| Case               | How it triggers                                          | Expected result                                 | Review SDK behavior                                                 |
|--------------------|----------------------------------------------------------|-------------------------------------------------|---------------------------------------------------------------------|
| `baseline`         | Real HTTP 200 firmware download                          | `ESP_OK` (`0`), `flash_begin=1`                 | Passes                                                              |
| `boot_error`       | Injected via `esp_ota_set_boot_partition` linker wrapper | `ESP_ERR_FLASH_OP_FAIL` (`24577`)               | Returns `0` (`ESP_OK`)                                              |
| `allocation_error` | Injected via `calloc` compile-time redirect              | `ESP_ERR_NO_MEM` (`257`)                        | Returns `-1` (`ESP_FAIL`)                                           |
| `http_404`         | Real HTTP 404 response                                   | `-1`, `flash_begin=0`                           | Calls `esp_ota_begin`, fails later (`5379`)                         |
| `http_500`         | Real HTTP 500 response                                   | `-1`, `flash_begin=0`                           | Calls `esp_ota_begin`, fails later (`5379`)                         |
| `stall_timeout`    | Real stalled HTTP 200 stream                             | `ESP_ERR_TIMEOUT` (`263`), `1..5` read timeouts | Loops through 14 timeouts (`v6.1.1` loops through 15), returns `-1` |

> [!NOTE]
> Results are from QEMU emulation (single-core FreeRTOS, plain HTTP over emulated Ethernet, disabled Timer Group watchdog), not physical hardware.
> Saved output for all three variants is in [docs/qemu-results.md](../../docs/qemu-results.md).

### How to Run

Run from the repository root inside `nix develop` on x86-64 Linux:

```sh
make setup        # Update the pinned SDKs and install or repair the tools
make test         # Build and run both the review SDK and v6.1.1 suites
make test-buggy   # Run only the review SDK suite (expects baseline pass plus 5 failures)
make test-fixed   # Run the generated fixed review SDK suite (expects all 6 passes)
make test-newest  # Run only the ESP-IDF v6.1.1 suite (expects 5 passes and stall_timeout fail)
```

Run the host unit tests after `make setup`.

```sh
build/ota-qemu/venv/bin/python -m unittest discover -s tests/reproduce-bugs/test -p 'test_*.py'
```
