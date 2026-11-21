#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include "esp_event.h"
#include "esp_https_ota.h"
#include "esp_idf_version.h"
#include "esp_netif.h"
#include "esp_ota_ops.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "protocol_examples_common.h"
#if ESP_IDF_VERSION_MAJOR >= 6
#include "spi_flash_mmap.h"
#else
#include "esp_spi_flash.h"
#endif

static bool fail_allocation;
static bool fail_boot_selection;
static unsigned allocations_failed;
static unsigned boot_failures_injected;
static unsigned flash_begin_calls;
static unsigned read_timeouts;
static int http_status;

int __real_esp_http_client_get_status_code(esp_http_client_handle_t client);
int __wrap_esp_http_client_get_status_code(esp_http_client_handle_t client)
{
    http_status = __real_esp_http_client_get_status_code(client);
    return http_status;
}

int __real_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int len);
int __wrap_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int len)
{
    int res = __real_esp_http_client_read(client, buffer, len);
#if ESP_IDF_VERSION_MAJOR >= 6
    if (res == -ESP_ERR_HTTP_EAGAIN) {
        ++read_timeouts;
    }
#else
    if (res == 0 && !esp_http_client_is_complete_data_received(client)) {
        ++read_timeouts;
    }
#endif
    return res;
}

void *ota_test_calloc(size_t count, size_t size)
{
    if (fail_allocation) {
        ++allocations_failed;
        return NULL;
    }
    return calloc(count, size);
}

esp_err_t __real_esp_ota_set_boot_partition(const esp_partition_t *partition);
esp_err_t __wrap_esp_ota_set_boot_partition(const esp_partition_t *partition)
{
    if (fail_boot_selection) {
        ++boot_failures_injected;
        return ESP_ERR_FLASH_OP_FAIL;
    }
    return __real_esp_ota_set_boot_partition(partition);
}

esp_err_t __real_esp_ota_begin(const esp_partition_t *partition, size_t size,
                             esp_ota_handle_t *handle);
esp_err_t __wrap_esp_ota_begin(const esp_partition_t *partition, size_t size,
                             esp_ota_handle_t *handle)
{
    ++flash_begin_calls;
    return __real_esp_ota_begin(partition, size, handle);
}

static void run_case(const char *name, const char *path, esp_err_t expected,
                     unsigned expected_flash_calls, int expected_http_status,
                     int timeout_ms, bool expect_timeout)
{
    char url[128];
    snprintf(url, sizeof(url), "http://10.0.2.2:18080/%s", path);
    esp_http_client_config_t config = {
        .url = url,
        .timeout_ms = timeout_ms,
    };
    allocations_failed = boot_failures_injected = flash_begin_calls = read_timeouts = 0;
    http_status = 0;
    printf("CASE_START %s\n", name);
#if ESP_IDF_VERSION_MAJOR >= 6
    esp_https_ota_config_t ota_config = { .http_config = &config };
    esp_err_t actual = esp_https_ota(&ota_config);
#else
    esp_err_t actual = esp_https_ota(&config);
#endif
    bool injected = (!fail_allocation || allocations_failed == 1) &&
                    (!fail_boot_selection || boot_failures_injected == 1);
    bool timeout_ok = !expect_timeout || (read_timeouts >= 1 && read_timeouts <= 5);
    bool passed = actual == expected && flash_begin_calls == expected_flash_calls &&
                  http_status == expected_http_status && injected && timeout_ok;
    printf("CASE_RESULT %s %s actual=%d expected=%d flash_begin=%u expected_flash_begin=%u allocation_failures=%u boot_failures=%u http_status=%d read_timeouts=%u\n",
           name, passed ? "PASS" : "FAIL", actual, expected, flash_begin_calls,
           expected_flash_calls, allocations_failed, boot_failures_injected,
           http_status, read_timeouts);
    fflush(stdout);
}

void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(example_connect());

    run_case("baseline", "image.bin", ESP_OK, 1, 200, 1000, false);
    fail_boot_selection = true;
    run_case("boot_error", "image.bin", ESP_ERR_FLASH_OP_FAIL, 1, 200, 1000, false);
    fail_boot_selection = false;
    fail_allocation = true;
    run_case("allocation_error", "image.bin", ESP_ERR_NO_MEM, 0, 0, 1000, false);
    fail_allocation = false;
    run_case("http_404", "404", ESP_FAIL, 0, 404, 1000, false);
    run_case("http_500", "500", ESP_FAIL, 0, 500, 1000, false);
    run_case("stall_timeout", "stall", ESP_ERR_TIMEOUT, 1, 200, 500, true);
    printf("SUITE_DONE\n");
    fflush(stdout);
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
