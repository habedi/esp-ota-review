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
#ifdef OTA_REPRO_CONSOLE
#include <string.h>
#include "driver/uart.h"
#include "esp_system.h"
#include "linenoise/linenoise.h"
#if ESP_IDF_VERSION_MAJOR >= 6
#include "driver/uart_vfs.h"
#else
#include "esp_vfs_dev.h"
#endif
#endif

static bool fail_allocation;
static bool fail_boot_selection;
static unsigned allocations_failed;
static unsigned boot_failures_injected;
static unsigned flash_begin_calls;
static unsigned read_timeouts;
static int http_status;

int __real_esp_http_client_get_status_code(esp_http_client_handle_t client);

int __wrap_esp_http_client_get_status_code(esp_http_client_handle_t client) {
    http_status = __real_esp_http_client_get_status_code(client);
    return http_status;
}

int __real_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int len);

int __wrap_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int len) {
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

void *ota_test_calloc(size_t count, size_t size) {
    if (fail_allocation) {
        ++allocations_failed;
        return NULL;
    }
    return calloc(count, size);
}

esp_err_t __real_esp_ota_set_boot_partition(const esp_partition_t *partition);

esp_err_t __wrap_esp_ota_set_boot_partition(const esp_partition_t *partition) {
    if (fail_boot_selection) {
        ++boot_failures_injected;
        return ESP_ERR_FLASH_OP_FAIL;
    }
    return __real_esp_ota_set_boot_partition(partition);
}

esp_err_t __real_esp_ota_begin(const esp_partition_t *partition, size_t size,
                               esp_ota_handle_t *handle);

esp_err_t __wrap_esp_ota_begin(const esp_partition_t *partition, size_t size,
                               esp_ota_handle_t *handle) {
    ++flash_begin_calls;
    return __real_esp_ota_begin(partition, size, handle);
}

static void run_case(const char *name, const char *path, esp_err_t expected,
                     unsigned expected_flash_calls, int expected_http_status,
                     int timeout_ms, bool expect_timeout) {
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
    esp_https_ota_config_t ota_config = {.http_config = &config};
    esp_err_t actual = esp_https_ota(&ota_config);
#else
    esp_err_t actual = esp_https_ota(&config);
#endif
    bool injected = (!fail_allocation || allocations_failed == 1) &&
                    (!fail_boot_selection || boot_failures_injected == 1);
    bool timeout_ok = !expect_timeout || (read_timeouts >= 1 && read_timeouts <= 5);
    bool passed = actual == expected && flash_begin_calls == expected_flash_calls &&
                  http_status == expected_http_status && injected && timeout_ok;
    printf(
        "CASE_RESULT %s %s actual=%d expected=%d flash_begin=%u expected_flash_begin=%u allocation_failures=%u boot_failures=%u http_status=%d read_timeouts=%u\n",
        name, passed ? "PASS" : "FAIL", actual, expected, flash_begin_calls,
        expected_flash_calls, allocations_failed, boot_failures_injected,
        http_status, read_timeouts);
    fflush(stdout);
}

static void run_suite(void) {
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
}

#ifdef OTA_REPRO_CONSOLE
static void print_state(void) {
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *boot = esp_ota_get_boot_partition();
    const esp_partition_t *next = esp_ota_get_next_update_partition(NULL);
    printf("running=%s boot=%s next_update=%s free_heap_bytes=%lu\n",
           running ? running->label : "none", boot ? boot->label : "none",
           next ? next->label : "none", (unsigned long)esp_get_free_heap_size());
}

static void run_console(void) {
    int uart = CONFIG_ESP_CONSOLE_UART_NUM;
    ESP_ERROR_CHECK(uart_driver_install(uart, 256, 0, 0, NULL, 0));
#if ESP_IDF_VERSION_MAJOR >= 6
    uart_vfs_dev_port_set_rx_line_endings(uart, ESP_LINE_ENDINGS_CR);
    uart_vfs_dev_use_driver(uart);
#else
    esp_vfs_dev_uart_port_set_rx_line_endings(uart, ESP_LINE_ENDINGS_CR);
    esp_vfs_dev_uart_use_driver(uart);
#endif

    linenoiseSetDumbMode(1);
    bool suite_done = false;
    puts("Type help for commands.");
    while (true) {
        char *command = linenoise("esp32> ");
        if (command == NULL) {
            continue;
        }
        if (strcmp(command, "state") == 0) {
            print_state();
        } else if (strcmp(command, "clear") == 0) {
            linenoiseClearScreen();
        } else if (strcmp(command, "run") == 0) {
            if (suite_done) {
                puts("The suite already ran. Start a fresh QEMU session to run it again.");
            } else {
                run_suite();
                suite_done = true;
            }
        } else if (strcmp(command, "help") == 0) {
            puts("state  Show OTA partitions and free heap\n"
                 "run    Run the OTA suite once\n"
                 "clear  Clear the console screen");
        } else if (*command) {
            puts("Unknown command. Type help for commands.");
        }
        linenoiseFree(command);
    }
}
#endif

void app_main(void) {
#ifdef OTA_REPRO_CONSOLE
    // Let the UART line editor read and echo each key before Enter.
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
#endif
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(example_connect());

#ifdef OTA_REPRO_CONSOLE
    run_console();
#else
    run_suite();
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
#endif
}
