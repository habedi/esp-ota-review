## The (Potential) Bugs

I checked the code and found a few potential bugs in the OTA solution.
I created a test for each bug and ran it on the version of the code that is checked out in `external/esp-idf-review` and `external/esp-idf-v6.1.1`.

The information about the versions of the ESP-IDF SDK that are pinned as Git submodules (in `external/`):

| Checkout                  | Revision                                                  |
|---------------------------|-----------------------------------------------------------|
| `external/esp-idf-review` | `7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00` (tag `v4.2.1`) |
| `external/esp-idf-v6.1.1` | `051e4c4eb20346e043cdd47bc388fde75ff8af63` (tag `v6.1.1`) |

| Bug title | Bug description | Fix verified | Was reported? |
|---|---|---|---|
| Boot selection fails, but OTA reports success | In `esp_https_ota_finish()` ([L340-L366](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L340-L366)), a new inner `err` variable hides the outer one at [L360](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L360). If `esp_ota_set_boot_partition()` fails, the error is only logged and the function returns `ESP_OK`. | [v5.1.3](https://github.com/espressif/esp-idf/commit/d778b07b2213370e1603d1aadf7b60393b3f7569) on the 5.1 branch | [#12635](https://github.com/espressif/esp-idf/issues/12635) (exact) |
| Initialization loses the specific error | In `esp_https_ota()` ([L392-L396](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L392-L396)), when `esp_https_ota_begin()` fails, the wrapper returns `ESP_FAIL` instead of the real error. This breaks the documented contract in `esp_https_ota.h` (L53-L60) and hides `ESP_ERR_NO_MEM` and `ESP_ERR_INVALID_ARG` from retry logic. | [v6.1.1](https://github.com/espressif/esp-idf/blob/v6.1.1/components/esp_https_ota/src/esp_https_ota.c#L1099-L1102) | No exact report found |
| HTTP errors can start a flash update | `_http_handle_response_code()` ([L60-L110](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L60-L110)) returns `ESP_OK` for HTTP 404 and 500. OTA then calls `esp_ota_begin()` ([L271](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L271)), which erases the passive OTA slot, and only fails later at image validation. HTTP 401 can also retry without a limit in `_http_connect()`. | [v4.4](https://github.com/espressif/esp-idf/commit/3c7991813d8a8f47009305a63d7d8d0d422fb8fb) source | [#7058](https://github.com/espressif/esp-idf/issues/7058), [#8195](https://github.com/espressif/esp-idf/issues/8195) (related) |
| The wrapper has no overall deadline | `esp_https_ota_perform()` ([L285-L306](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L285-L306)) returns `ESP_ERR_HTTPS_OTA_IN_PROGRESS` on a read timeout (or `-ESP_ERR_HTTP_EAGAIN` in `v6.1.1`). `esp_https_ota()` loops on this in `while (1)` ([L398-L403](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c#L398-L403)) with no total time limit. Over plain TCP, a clean peer close returns `-1` in `tcp_read()`, whereas a stalled HTTP stream loops through repeated read timeouts on both `7ad199d14a` (`14` timeouts in QEMU) and `v6.1.1` (`15` timeouts in QEMU) until the server drops the connection. | Not fixed in `v6.1.1`; local fix verified in QEMU | [#6364](https://github.com/espressif/esp-idf/issues/6364) |

### Other Related Issues

[Related ESP-IDF OTA Issues](related-issues.md) covers findings from upstream issue reports and source review of `v4.2.1` and `v6.1.1`.
