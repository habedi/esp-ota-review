## Ideas for R&D

### Bounded Model Checking for OTA

CBMC checks C assertions across all inputs and failure outcomes allowed by a harness, within a set bound.
If a check fails, it reports the inputs and steps that triggered the failure. [CBMC documentation](https://www.cprover.org/cbmc/)

#### Boot-Selection Errors

Check that `esp_https_ota_finish()` returns the result of `esp_ota_set_boot_partition()` when image finalization succeeds.
The harness can call the real finish function and let the boot-selection stub return any supported result.

The pinned SDK (`7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00`) should fail the check because an inner variable hides the error.
The same harness should pass against the fixed copy generated in the build directory. [OTA bug notes](bugs.md)

#### Download Deadline

Model the clock and HTTP reads so that small chunks can arrive often enough to keep the idle timeout from firing.
Check that the wrapper returns `ESP_ERR_TIMEOUT` at the first deadline check after the total time limit expires.
The existing QEMU test covers idle timeouts.
A wall-clock guarantee also depends on which phases the deadline covers and how long each call can block. [OTA bug notes](bugs.md)

#### Power-Loss Recovery

With rollback enabled and a known-good image available, model a power cut during each flash erase or write that updates OTA metadata.
Include the partial erase and write outcomes the flash allows.
Check that the bootloader can still find a bootable image and that a reset while the new image is pending verification brings back the previous image.
Physical board tests can check the flash assumptions. [ESP-IDF OTA guide](https://docs.espressif.com/projects/esp-idf/en/v4.2.1/esp32/api-reference/system/ota.html)

#### Scope

These checks are proposals.
Record the SDK revision, configuration, modeled inputs, and bounds for each run.
Enable unwinding assertions to catch loop bounds that are too low. [CBMC manual](https://www.cprover.org/cbmc/doc/manual.pdf)

The existing QEMU runs used single-core ESP32 emulation, plain HTTP, and disabled Timer Group watchdogs. [QEMU results](qemu-results.md)
