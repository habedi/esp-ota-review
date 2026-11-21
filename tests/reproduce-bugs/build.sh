#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
variant=${1:?Usage: bash tests/reproduce-bugs/build.sh original|fixed|v6.1.1}
build_dir="$PWD/build/ota-qemu/$variant"
case "$variant" in
    original|fixed)
        sdk=esp-idf-review
        revision=7ad199d14a5d0fd2f61193c0f8a51a5d2bfa2c00
        ;;
    v6.1.1)
        sdk=esp-idf-v6.1.1
        revision=051e4c4eb20346e043cdd47bc388fde75ff8af63
        ;;
    *) echo 'Expected original, fixed, or v6.1.1' >&2; exit 2 ;;
esac
export IDF_PATH="$PWD/external/$sdk"
if [[ "$(git -C "$IDF_PATH" rev-parse HEAD)" != "$revision" ]]; then
    echo "Expected $sdk at $revision. Run make setup (or git submodule update --init --recursive --depth 1 --single-branch --filter=blob:none)." >&2
    exit 1
fi
git -C "$IDF_PATH" diff --exit-code HEAD -- components/esp_https_ota

export PATH="$PWD/build/ota-qemu/venv/bin:$PATH"
if [[ "$variant" == v6.1.1 ]]; then
    export IDF_TOOLS_PATH="$PWD/build/ota-qemu/tools-v6.1.1"
    set +u
    source "$IDF_PATH/export.sh"
    set -u
    idf.py -C tests/reproduce-bugs -B "$build_dir" \
        -D "SDKCONFIG=$build_dir/sdkconfig" \
        -D 'SDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.v6.1.1' build
else
    export IDF_TOOLS_PATH="$PWD/build/ota-qemu/tools"
    export PATH="$IDF_TOOLS_PATH/tools/xtensa-esp32-elf/esp-2020r3-8.4.0/xtensa-esp32-elf/bin:$PATH"
    fixed=OFF
    if [[ "$variant" == fixed ]]; then fixed=ON; fi
    cmake -S tests/reproduce-bugs -B "$build_dir" -G Ninja \
        -D SDKCONFIG="$build_dir/sdkconfig" \
        -D CMAKE_POLICY_VERSION_MINIMUM=3.5 -D PYTHON_DEPS_CHECKED=1 \
        -D OTA_REPRO_FIXED="$fixed"
    cmake --build "$build_dir" -j 8
fi
