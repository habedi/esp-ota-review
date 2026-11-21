## Zaptec's Case (ESP-IDF OTA Reliability Review)

[![Tests](https://img.shields.io/github/actions/workflow/status/habedi/esp-ota-review/tests.yml?label=tests&style=flat&labelColor=282c34&logo=github&logoColor=white)](https://github.com/habedi/esp-ota-review/actions/workflows/tests.yml)
[![Documentation](https://img.shields.io/badge/docs-latest-507ec6?style=flat&labelColor=282c34&logo=read-the-docs&logoColor=white)](docs)
[![License](https://img.shields.io/badge/license-Apache--2.0-507ec6?style=flat&labelColor=282c34&logo=open-source-initiative&logoColor=white)](LICENSE)

Review
the [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c)
and [simple_ota_example.c](https://github.com/espressif/esp-idf/blob/07bfc09d0c8837b4d149e1151c57635a0c02755a/examples/system/ota/simple_ota_example/main/simple_ota_example.c).
(The first file implements the over-the-air (OTA) update and the second file shows an example use case of the OTA solution.)
Then answer the following questions:

1. Are there bugs in the OTA implementation?
2. What can go wrong when calling `esp_https_ota` wrapper function as it is implemented?
3. How should we use the `esp_https_ota` function in order to ensure sufficient robustness? Is it even possible?
4. How would we work to make sure that the OTA solution in the product is robust enough?

**Follow the steps in [Quickstart](#quickstart) section and check out the presentation [slides](#4-build-the-presentation) for answers and
explanations.**

---

### Quickstart

To follow the steps below, you need to have Git and [Nix](https://nixos.org/download/) (with flakes enabled) installed on your machine.

#### 1. Clone the repository

```shell
git clone --depth 1 https://github.com/habedi/esp-ota-review.git
cd esp-ota-review
```

#### 2. Set up the development environment

```shell
nix develop

# Check the SDK revisions and install or repair the tools
make setup
```

#### 3. Run the tests to show the bugs

```bash
# This may take a while to run
make test
```

After the tests ran, the results will be stored in `build/ota-qemu/` as two CSV files.

> [!IMPORTANT]
> This step needs an x86-64 Linux machine to run.

#### 4. Build the presentation

```bash
make pres
```

The presentation will be available as `build/presentation/zaptec-tech-case-pres.pdf`.

---

### License

The content of this repository is licensed under the Apache License, Version 2.0 (see [LICENSE](LICENSE)).
