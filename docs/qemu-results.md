## QEMU OTA Results

All three runs used single-core ESP32 QEMU, HTTP over emulated Ethernet, and disabled QEMU Timer Group watchdogs.

### Original

```text
CASE_RESULT baseline PASS actual=0 expected=0 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=0 http_status=200 read_timeouts=0
CASE_RESULT boot_error FAIL actual=0 expected=24577 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=1 http_status=200 read_timeouts=0
CASE_RESULT allocation_error FAIL actual=-1 expected=257 flash_begin=0 expected_flash_begin=0 allocation_failures=1 boot_failures=0 http_status=0 read_timeouts=0
CASE_RESULT http_404 FAIL actual=5379 expected=-1 flash_begin=1 expected_flash_begin=0 allocation_failures=0 boot_failures=0 http_status=404 read_timeouts=0
CASE_RESULT http_500 FAIL actual=5379 expected=-1 flash_begin=1 expected_flash_begin=0 allocation_failures=0 boot_failures=0 http_status=500 read_timeouts=0
CASE_RESULT stall_timeout FAIL actual=-1 expected=263 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=0 http_status=200 read_timeouts=14
SUITE_DONE
```

### Fixed

```text
CASE_RESULT baseline PASS actual=0 expected=0 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=0 http_status=200 read_timeouts=0
CASE_RESULT boot_error PASS actual=24577 expected=24577 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=1 http_status=200 read_timeouts=0
CASE_RESULT allocation_error PASS actual=257 expected=257 flash_begin=0 expected_flash_begin=0 allocation_failures=1 boot_failures=0 http_status=0 read_timeouts=0
CASE_RESULT http_404 PASS actual=-1 expected=-1 flash_begin=0 expected_flash_begin=0 allocation_failures=0 boot_failures=0 http_status=404 read_timeouts=0
CASE_RESULT http_500 PASS actual=-1 expected=-1 flash_begin=0 expected_flash_begin=0 allocation_failures=0 boot_failures=0 http_status=500 read_timeouts=0
CASE_RESULT stall_timeout PASS actual=263 expected=263 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=0 http_status=200 read_timeouts=4
SUITE_DONE
```

### v6.1.1

```text
CASE_RESULT baseline PASS actual=0 expected=0 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=0 http_status=200 read_timeouts=0
CASE_RESULT boot_error PASS actual=24577 expected=24577 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=1 http_status=200 read_timeouts=0
CASE_RESULT allocation_error PASS actual=257 expected=257 flash_begin=0 expected_flash_begin=0 allocation_failures=1 boot_failures=0 http_status=0 read_timeouts=0
CASE_RESULT http_404 PASS actual=-1 expected=-1 flash_begin=0 expected_flash_begin=0 allocation_failures=0 boot_failures=0 http_status=404 read_timeouts=0
CASE_RESULT http_500 PASS actual=-1 expected=-1 flash_begin=0 expected_flash_begin=0 allocation_failures=0 boot_failures=0 http_status=500 read_timeouts=0
CASE_RESULT stall_timeout FAIL actual=-1 expected=263 flash_begin=1 expected_flash_begin=1 allocation_failures=0 boot_failures=0 http_status=200 read_timeouts=15
SUITE_DONE
```
