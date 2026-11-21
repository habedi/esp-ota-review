## Related ESP-IDF OTA Issues

|  # | Item                                                                                                                                                                                                                                                                       | Status                                      | Presence in `v4.2.1` and `v6.1.1`                       | Relevance                                                                      |
|---:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|---------------------------------------------------------|--------------------------------------------------------------------------------|
|  1 | Commit [eef3b0bf](https://github.com/espressif/esp-idf/commit/eef3b0bf)                                                                                                                                                                                                    | Fixed                                       | Present in `v4.2.1`; fixed in `v6.1.1`                  | Allows plain HTTP URLs or HTTPS-to-HTTP downgrade redirects                    |
|  2 | Commit [2d7ec1d2](https://github.com/espressif/esp-idf/commit/2d7ec1d2) and redirect loop                                                                                                                                                                                  | Fixed for HTTP 401; unguarded for redirects | Present in `v4.2.1`; redirect check missing in `v6.1.1` | Loops without limit on HTTP 401 or cyclical redirects                          |
|  3 | Issue [#5504](https://github.com/espressif/esp-idf/issues/5504) (commit [48987ad9](https://github.com/espressif/esp-idf/commit/48987ad9))                                                                                                                                  | Closed                                      | Present in `v4.2.1`; fixed in `v6.1.1`                  | Blocks certificate bundle and global certificate authority store               |
|  4 | Commits [1c57dbcb](https://github.com/espressif/esp-idf/commit/1c57dbcb) and [7115881a](https://github.com/espressif/esp-idf/commit/7115881a)                                                                                                                              | Fixed                                       | Present in `v4.2.1`; fixed in `v6.1.1`                  | Inspects stale `errno` values and mishandles socket timeouts                   |
|  5 | Commits [33d00240](https://github.com/espressif/esp-idf/commit/33d00240) and [bc78b8f2](https://github.com/espressif/esp-idf/commit/bc78b8f2)                                                                                                                              | Fixed                                       | Present in `v4.2.1`; fixed in `v6.1.1`                  | Erases full slot upfront and validates aborted downloads                       |
|  6 | Issue [#8581](https://github.com/espressif/esp-idf/issues/8581) ([d5a8a576](https://github.com/espressif/esp-idf/commit/d5a8a576)), [4ae6cce2](https://github.com/espressif/esp-idf/commit/4ae6cce2), and [85f919a4](https://github.com/espressif/esp-idf/commit/85f919a4) | Closed and fixed                            | Present in `v4.2.1`; fixed in `v6.1.1`                  | Missing HTTP 303 and 308 redirects, descriptor magic check, and log formatting |
|  7 | Issue [#18127](https://github.com/espressif/esp-idf/issues/18127)                                                                                                                                                                                                          | Closed                                      | Present in `v4.2.1`; fixed in `v6.1.1`                  | Allows concurrent OTA handles on the same partition                            |
|  8 | Issue [#19413](https://github.com/espressif/esp-idf/issues/19413)                                                                                                                                                                                                          | Open                                        | Present in `v4.2.1`; present in `v6.1.1`                | Returns `ESP_OK` on retry without confirming the running application           |
|  9 | Issue [#14688](https://github.com/espressif/esp-idf/issues/14688)                                                                                                                                                                                                          | Closed                                      | Present in `v4.2.1`; fixed in `v6.1.1`                  | Loses running partition state after two updates without a reboot               |
| 10 | Issues [#10890](https://github.com/espressif/esp-idf/issues/10890) and [#14450](https://github.com/espressif/esp-idf/issues/14450)                                                                                                                                         | Open                                        | Hardware timing risk (untested in QEMU)                 | Triggers watchdog resets during flash erase and write operations               |
| 11 | Issue [#10437](https://github.com/espressif/esp-idf/issues/10437)                                                                                                                                                                                                          | Closed                                      | Present in `v4.2.1`; fixed in `v6.1.1`                  | Crashes during flash writes when task stack sits in external SPI RAM           |
| 12 | Issue [#16968](https://github.com/espressif/esp-idf/issues/16968)                                                                                                                                                                                                          | Open                                        | More severe in `v4.2.1`; partial in `v6.1.1`            | Fails `bootloader_mmap()` with `ESP_ERR_NO_MEM` and can trigger Bug 1          |
| 13 | Issues [#9987](https://github.com/espressif/esp-idf/issues/9987) and [#17595](https://github.com/espressif/esp-idf/issues/17595)                                                                                                                                           | Closed                                      | Cross-version field upgrade hazard                      | Breaks upgrades across partition table MD5 or bootloader changes               |
| 14 | Issue [#13065](https://github.com/espressif/esp-idf/issues/13065)                                                                                                                                                                                                          | Closed                                      | Fixed in `v6.1.1`                                       | Corrupted firmware with `partial_http_download` in intermediate releases       |
| 15 | Issue [#19439](https://github.com/espressif/esp-idf/issues/19439)                                                                                                                                                                                                          | Open                                        | Not in `v4.2.1`; present in `v6.1.1`                    | Leaves partition locked on erase failure in `esp_ota_begin()` until reboot     |
| 16 | Issue [#10996](https://github.com/espressif/esp-idf/issues/10996)                                                                                                                                                                                                          | Closed (`Resolution: NA`)                   | Excluded (application web server code)                  | Failed multipart upload parsing outside `esp_https_ota`                        |

### Additional Bugs in `esp_https_ota.c` at `7ad199d14a`

- Plain HTTP and HTTPS downgrade allowed:
  in [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L147-L153),
  `esp_https_ota_begin()` checks only that `cert_pem` is non-null when `CONFIG_OTA_ALLOW_HTTP` is off. It does not check `transport_type` or the URL
  scheme. Passing an `http://` URL or redirecting from HTTPS to `http://`
  switches [esp_http_client.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_http_client/esp_http_client.c#L767-L776)
  and [esp_http_client.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_http_client/esp_http_client.c#L1070)
  to plain TCP. Commit [eef3b0bf](https://github.com/espressif/esp-idf/commit/eef3b0bf) fixed this by pinning SSL transport and rejecting non-HTTPS
  redirects. Those guards are present in `v6.1.1`
  at [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_https_ota/src/esp_https_ota.c#L313-L345)
  and [esp_http_client.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_http_client/esp_http_client.c#L1173-L1180).
- Unbounded HTTP 401 and redirect loops: `_http_connect()`
  at [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L90-L111)
  loops while `process_again(status_code)` is true. HTTP 401 has no retry limit in `v4.2.1`;
  commit [2d7ec1d2](https://github.com/espressif/esp-idf/commit/2d7ec1d2) later added `max_authorization_retries`. Redirect limits are also unenforced
  in this path. `esp_http_client_set_redirection()` does not check `max_redirection_count` or `disable_auto_redirect` in `v4.2.1`
  ([esp_http_client.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_http_client/esp_http_client.c#L685-L695)),
  and in `v6.1.1` `_http_handle_response_code()`
  ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_https_ota/src/esp_https_ota.c#L107-L112)) still calls
  `esp_http_client_set_redirection()`
  ([esp_http_client.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_http_client/esp_http_client.c#L1160-L1188)) outside
  `esp_http_check_response()`
  ([esp_http_client.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_http_client/esp_http_client.c#L1199-L1233)). A cyclical
  redirect can keep `_http_connect()` looping.
- Certificate bundle and global certificate authority store blocked: issue [#5504](https://github.com/espressif/esp-idf/issues/5504) (closed), fixed
  in commit [48987ad9](https://github.com/espressif/esp-idf/commit/48987ad9). Because `v4.2.1` requires `cert_pem`
  at [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L148),
  configurations using `use_global_ca_store` or `crt_bundle_attach` fail unless a dummy certificate is supplied. This makes certificate rotation
  harder on deployed devices. `v6.1.1` accepts all three verification options in `is_server_verification_enabled()`
  ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_https_ota/src/esp_https_ota.c#L299-L303)).
- Stale `errno` checks and `EAGAIN` handling: commits [1c57dbcb](https://github.com/espressif/esp-idf/commit/1c57dbcb)
  and [7115881a](https://github.com/espressif/esp-idf/commit/7115881a) addressed how read timeouts and TLS want-read states were reported. In
  `v4.2.1`, [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L239)
  and [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L301)
  inspect global `errno` without clearing it beforehand, which feeds directly into the stall path in Bug 4 and
  issue [#6364](https://github.com/espressif/esp-idf/issues/6364).
- Full-partition erase and missing abort API: commits [33d00240](https://github.com/espressif/esp-idf/commit/33d00240)
  and [bc78b8f2](https://github.com/espressif/esp-idf/commit/bc78b8f2) updated flash erase behavior and cleanup. In `v4.2.1`,
  `esp_https_ota_perform()` passes `OTA_SIZE_UNKNOWN` to `esp_ota_begin()`
  ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L271)).
  That erases the entire passive slot upfront instead of erasing sector by sector during writes. `v4.2.1` also lacks `esp_https_ota_abort()`, so
  `esp_https_ota()` calls `esp_https_ota_finish()`
  ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L405))
  even when the download fails, and runs full flash verification on broken transfers. Both improvements are in `v6.1.1`
  ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_https_ota/src/esp_https_ota.c#L794-L801)
  and [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_https_ota/src/esp_https_ota.c#L1115-L1118)).
- Smaller fixes after `v4.2.1`: issue [#8581](https://github.com/espressif/esp-idf/issues/8581) and
  commit [d5a8a576](https://github.com/espressif/esp-idf/commit/d5a8a576) add HTTP 303 and 308 redirects;
  commit [4ae6cce2](https://github.com/espressif/esp-idf/commit/4ae6cce2) validates `ESP_APP_DESC_MAGIC_WORD` in `esp_https_ota_get_img_desc()`
  ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L251));
  commit [85f919a4](https://github.com/espressif/esp-idf/commit/85f919a4) fixes malformed `0x%d` format strings
  at [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L126)
  and [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L362).

### Low-level `esp_ota_ops` and Runtime Issues

- No concurrent OTA lock in `v4.2.1`: issue [#18127](https://github.com/espressif/esp-idf/issues/18127) (closed). In `v4.2.1`, `esp_ota_begin()`
  ([esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/app_update/esp_ota_ops.c#L129-L190))
  does not reject a second handle opened on the same target partition. Products that support updates over both HTTPS and Bluetooth must serialize OTA
  in application code. `v6.1.1` checks `esp_ota_check_partition_conflict()`
  ([esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/app_update/esp_ota_ops.c#L190-L193)).
- Rollback confirmation bug after a failed `otadata` write: issue [#19413](https://github.com/espressif/esp-idf/issues/19413) (open).
  `esp_ota_mark_app_valid_cancel_rollback()` calls `esp_ota_current_ota_is_workable(true)`, which inspects and writes `otadata[active_otadata]`
  without verifying that the active entry points to the running partition ([v4.2.1
  `esp_ota_ops.c`](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/app_update/esp_ota_ops.c#L701-L712)
  and [v6.1.1 `esp_ota_ops.c`](https://github.com/espressif/esp-idf/blob/v6.1.1/components/app_update/esp_ota_ops.c#L1187-L1199)). After one failed
  `otadata` write, a retry can return `ESP_OK` while the running application remains unconfirmed and rolls back on reboot.
- Partition state lost after two updates without a reboot: issue [#14688](https://github.com/espressif/esp-idf/issues/14688) (closed). In `v4.2.1`,
  `esp_rewrite_ota_data()`
  ([esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/app_update/esp_ota_ops.c#L402-L411))
  alternates between the two `otadata` sectors on every `esp_ota_set_boot_partition()` call. That overwrites both sectors if two updates complete
  before a reboot. Because `esp_ota_get_state_partition()` reads only those two sectors
  ([esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/app_update/esp_ota_ops.c#L806-L813)),
  querying the running partition state then returns `ESP_ERR_NOT_FOUND`. `v6.1.1` reuses the active sector when the target slot already matches
  ([esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/app_update/esp_ota_ops.c#L795-L801)).
- Watchdog resets during flash erase and writes: issues [#10890](https://github.com/espressif/esp-idf/issues/10890)
  and [#14450](https://github.com/espressif/esp-idf/issues/14450) (both open). Flash operations disable flash cache and pause the other core, which
  can trigger interrupt or task watchdogs under real-time peripheral or wireless load. Because QEMU runs single-core with Timer Group watchdogs
  disabled, watchdog behavior during flash erases and writes must be tested on physical hardware.
- External SPI RAM task stack crashes: issue [#10437](https://github.com/espressif/esp-idf/issues/10437) (closed). Calling `esp_https_ota()` from a
  task whose stack is in external SPI RAM crashes inside `spi_flash_disable_interrupts_caches_and_other_cpu()` during flash operations. Keep OTA task
  stacks in internal RAM.
- Flash memory mapping failure during image verification: issue [#16968](https://github.com/espressif/esp-idf/issues/16968) (open). During
  `esp_ota_end()`, `esp_image_verify()` calls `process_segment()` and `bootloader_mmap()` to map large flash segments into virtual address space. In
  the report, mapping a 900-kilobyte segment failed with `spi_flash_mmap failed: 0x101` (`ESP_ERR_NO_MEM`), whereas smaller 256-kilobyte chunks
  succeeded. `v4.2.1` is more exposed because `spi_flash_mmap_get_free_pages()` counts total free MMU pages rather than the longest contiguous run
  ([flash_mmap.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/spi_flash/flash_mmap.c#L358-L376)
  and [flash_mmap.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/spi_flash/flash_mmap.c#L222-L225)),
  and `free_page_count - offset_page` lacks a zero guard
  ([esp_image_format.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/bootloader_support/src/esp_image_format.c#L543-L555)).
  `v6.1.1` checks the largest contiguous free block
  ([flash_mmap.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/spi_flash/flash_mmap.c#L597-L609)) and adds a zero-page check
  ([esp_image_format.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/bootloader_support/src/esp_image_format.c#L662-L699)), although
  free MMU space can still change before the map call runs. In both `v4.2.1`
  ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L344-L353))
  and `v6.1.1` ([esp_https_ota.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_https_ota/src/esp_https_ota.c#L982-L992)),
  `esp_https_ota_finish()` calls `esp_ota_end()` before freeing `ota_upgrade_buf` and the HTTP client, so verification runs at peak memory usage.
  Also, `esp_ota_end()` collapses any `esp_image_verify()` error to `ESP_ERR_OTA_VALIDATE_FAILED`
  ([esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/app_update/esp_ota_ops.c#L336-L339)),
  which masks memory or MMU failures as bad images. Finally, in `v4.2.1`, `esp_ota_set_boot_partition()` runs `image_validate()` a second time
  ([esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/app_update/esp_ota_ops.c#L426-L428));
  if `bootloader_mmap()` fails during that second validation pass, Bug 1 hides the failure and returns `ESP_OK`.

### Additional Findings

- Cross-version SDK upgrade hazards: issues [#9987](https://github.com/espressif/esp-idf/issues/9987)
  and [#17595](https://github.com/espressif/esp-idf/issues/17595) (both closed). Deployed units running older firmware and bootloaders can fail when
  upgraded across major ESP-IDF versions, for example due to partition table MD5 validation enforcement (`#9987`) or older bootloader versus newer
  application mismatches (`#17595`). Release testing must cover OTA upgrades starting from older field firmware images.
- Regressions in newer ESP-IDF OTA code: issue [#13065](https://github.com/espressif/esp-idf/issues/13065) (closed) corrupted firmware images when
  `partial_http_download` ran without calling `esp_https_ota_get_img_desc()` first. Issue [#19439](https://github.com/espressif/esp-idf/issues/19439)
  (open, visible in `v6.1.1` at [esp_ota_ops.c](https://github.com/espressif/esp-idf/blob/v6.1.1/components/app_update/esp_ota_ops.c#L195-L220))
  inserts the new entry into `s_ota_ops_entries_head` before calling `esp_partition_erase_range()`; if erase fails, `esp_ota_begin()` returns without
  removing the entry, which leaves the partition locked with `ESP_ERR_OTA_ALREADY_IN_PROGRESS` until reboot. Upgrading ESP-IDF removes older defects
  but still requires automated fault-injection tests around every production OTA path.

### Reviewed and Excluded Issues

- Custom web upload multipart bug: issue [#10996](https://github.com/espressif/esp-idf/issues/10996) (closed, `Resolution: NA`). The reporter
  implemented a custom ESP32-S3 HTTP server with `httpd_req_recv()` and called `esp_ota_begin()`, `esp_ota_write()`, and `esp_ota_end()` directly
  rather than `esp_https_ota()`. The upload handler searched for `"application/octet-stream"` to strip multipart form headers, missed the boundary,
  and fed `0x2d` (`-`) into `esp_ota_write()`. That call failed with `OTA image has invalid magic byte`. After calling `esp_ota_abort()`, the loop
  kept calling `esp_ota_write()`, `esp_ota_end()`, `esp_ota_set_boot_partition()`, and `esp_restart()`. In comments, the reporter resolved the issue
  by enabling `CONFIG_LWIP_L2_TO_L3_COPY`
  ([lwip Kconfig](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/lwip/Kconfig#L18-L32)). Aside from
  showing the same late magic-byte rejection in `esp_ota_write()` seen when HTTP 404 or 500 bodies reach flash in Bug 3, `#10996` is not an
  `esp_https_ota` defect and is excluded from our bug list.
