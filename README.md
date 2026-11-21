## Zaptec's Technical Case

First review
the [esp_https_ota.c](https://github.com/espressif/esp-idf/blob/7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00/components/esp_https_ota/src/esp_https_ota.c)
and [simple_ota_example.c](https://github.com/espressif/esp-idf/blob/07bfc09d0c8837b4d149e1151c57635a0c02755a/examples/system/ota/simple_ota_example/main/simple_ota_example.c).
(The first file implements the over-the-air (OTA) update and the second file shows an example use case of the OTA solution.)
Then try to answer the following questions:

1. Are there bugs in the OTA implementation?
2. What can go wrong when calling `esp_https_ota` wrapper function as it is implemented?
3. How should we use the `esp_https_ota` function in order to ensure sufficient robustness? Is it even possible?
4. How would we work to ensure that the OTA solution in the product is robust enough?

To answer these questions, I checked the code and found a few potential bugs (see [The (Potential) Bugs](docs/bugs.md#the-potential-bugs)).
Then I created a test for each bug and ran the tests on the version of the code that is checked out in `external/esp-idf-review` and
`external/esp-idf-v6.1.1`.

The information about the versions of the ESP-IDF SDK that are pinnd as Git submodules (in `external/`):

| Checkout                  | Revision                                                  |
|---------------------------|-----------------------------------------------------------|
| `external/esp-idf-review` | `7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00` (tag `v4.2.1`) |
| `external/esp-idf-v6.1.1` | `051e4c4eb20346e043cdd47bc388fde75ff8af63` (tag `v6.1.1`) |

---

### Quickstart

To follow the steps below, you need to have Git, GNU Make, and [Nix](https://nixos.org/download/) (with flakes enabled) installed on your machine.

#### 1. Clone the repository

```shell
git clone --depth 1 https://github.com/idea-playground/esp-https-ota
cd esp-https-ota
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

After the tests ran, the results will be stored in [build/ota-qemu/](build/ota-qemu/) as two CSV files.

> [!IMPORTANT]
> This step needs an x86-64 Linux host to run.

#### 4. Build the presentation

```bash
make pres
```

The presentation will be available [here](build/presentation/zaptec-tech-case-pres.pdf).

---

