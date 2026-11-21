idf_component_register(SRCS "main.c" REQUIRES esp_https_ota app_update protocol_examples_common nvs_flash spi_flash)
target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=esp_ota_set_boot_partition" "-Wl,--wrap=esp_ota_begin" "-Wl,--wrap=esp_http_client_get_status_code" "-Wl,--wrap=esp_http_client_read")
