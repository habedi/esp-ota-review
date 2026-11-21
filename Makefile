TESTS := tests/reproduce-bugs
BUILD := build/ota-qemu
PYTHON := $(BUILD)/venv/bin/python
QEMU := $(BUILD)/qemu/bin/qemu-system-xtensa
SLIDES := presentation/zaptec-tech-case-pres.tex
SLIDES_PDF := build/presentation/zaptec-tech-case-pres.pdf

.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
.PHONY: help pres hooks setup setup-host setup-sdks setup-newest force-python-sync
.PHONY: check-setup check-common check-review check-newest test test-buggy test-fixed test-newest clean distclean
# Both QEMU runs need the same local HTTP port.
.NOTPARALLEL:

test: test-buggy test-newest

help:
	@printf '%s\n' \
		'make help         Show this help' \
		'make setup        Install SDK submodules, Python venv, compilers, and QEMU' \
		'make pres         Build the interview slides (as a PDF file)' \
		'make hooks        Run the pre-commit hooks manually on all files' \
		'make test         Build and run the review SDK and v6.1.1 suites' \
		'make test-buggy   Run the tests for the buggy OTA component implementation' \
		'make test-fixed   Run the tests for the locally fixed OTA component implementation' \
		'make test-newest  Run the tests for the OTA component implementation from ESP-IDF v6.1.1' \
		'make clean        Remove build outputs, logs, and CSV results (keeps installed tools)' \
		'make distclean    Also remove the venv, compilers, and QEMU (need to run make setup again)' \
		'' \
		'On x86-64 Linux, enter `nix develop`, run `make setup`, then `make test`.' \
		'More details are in $(TESTS)/README.md.'

pres: $(SLIDES_PDF)
	@printf 'Presentation PDF is at %s\n' '$(SLIDES_PDF)'

$(SLIDES_PDF): $(SLIDES)
	mkdir -p $(@D)
	pdflatex -halt-on-error -interaction=nonstopmode -output-directory=$(@D) $<
	pdflatex -halt-on-error -interaction=nonstopmode -output-directory=$(@D) $<

hooks:
	uvx pre-commit run --hook-stage pre-push --all-files

SDK_REVIEW := external/esp-idf-review
SDK_NEWEST := external/esp-idf-v6.1.1
TOOLS := $(BUILD)/tools
TOOLS_NEWEST := $(BUILD)/tools-v6.1.1
CC_REVIEW := $(TOOLS)/tools/xtensa-esp32-elf/esp-2020r3-8.4.0/xtensa-esp32-elf/bin/xtensa-esp32-elf-gcc
PYTHON_STAMP := $(BUILD)/venv/.synced
NEWEST_ENV = PATH="$(abspath $(BUILD)/venv/bin):$$PATH" IDF_TOOLS_PATH="$(abspath $(TOOLS_NEWEST))"
NEWEST_TOOLS = $(NEWEST_ENV) "$(PYTHON)" "$(SDK_NEWEST)/tools/idf_tools.py" --idf-path "$(abspath $(SDK_NEWEST))"
NEWEST_CHECK = $(NEWEST_TOOLS) check && $(NEWEST_TOOLS) check-python-dependencies

setup-host:
	@test "$$(uname -s)" = Linux && test "$$(uname -m)" = x86_64 || { \
		echo 'OTA setup requires x86-64 Linux for the pinned QEMU build.' >&2; exit 1; \
	}

setup-sdks: setup-host
	git submodule update --init --recursive --checkout --depth 1 --single-branch --filter=blob:none

# The venv can lose its interpreter while the dependency stamp still exists.
ifeq ($(shell test -x "$(PYTHON)" && printf yes),)
$(PYTHON_STAMP): force-python-sync
endif

$(PYTHON_STAMP): $(TESTS)/requirements.txt | setup-host
	rm -f "$@"
	uv venv --allow-existing --python 3.10.20 "$(BUILD)/venv"
	uv pip sync --python "$(PYTHON)" "$(TESTS)/requirements.txt"
	touch "$@"

$(CC_REVIEW): | setup-sdks $(PYTHON_STAMP)
	IDF_TOOLS_PATH="$(abspath $(TOOLS))" "$(PYTHON)" "$(SDK_REVIEW)/tools/idf_tools.py" install xtensa-esp32-elf

setup-newest: | setup-sdks $(PYTHON_STAMP)
	@if ! ( $(NEWEST_CHECK) ) >/dev/null 2>&1; then \
		$(NEWEST_ENV) bash "$(SDK_NEWEST)/install.sh" esp32 && ( $(NEWEST_CHECK) ); \
	fi

$(SDK_NEWEST)/tools/tools.json: | setup-sdks

# Tar restores the binary's release timestamp.
$(QEMU): $(TESTS)/install_qemu.py $(SDK_NEWEST)/tools/tools.json | $(PYTHON_STAMP)
	"$(PYTHON)" "$<"
	touch "$@"

setup: setup-sdks $(CC_REVIEW) setup-newest $(QEMU)
	@echo 'Setup is complete. Run make test.'

check-setup: check-review check-newest

check-common:
	@for f in "$(PYTHON)" "$(QEMU)"; do \
		test -x "$$f" || { echo "Missing or unusable $$f. Run make setup first." >&2; exit 1; }; \
	done

check-review: check-common
	@test -x "$(CC_REVIEW)" || { echo 'Missing or unusable review compiler. Run make setup first.' >&2; exit 1; }

check-newest: check-common
	@( $(NEWEST_CHECK) ) >/dev/null || { echo 'ESP-IDF v6.1.1 tools need setup. Run make setup first.' >&2; exit 1; }

test-buggy: VARIANT := original
test-buggy: EXPECT := --expect-buggy
test-fixed: VARIANT := fixed
test-fixed: EXPECT :=
test-newest: VARIANT := v6.1.1
test-newest: EXPECT := --expect-fail stall_timeout

test-buggy test-fixed: check-review
test-newest: check-newest

test-buggy test-fixed test-newest:
	bash $(TESTS)/build.sh $(VARIANT)
	$(PYTHON) $(TESTS)/test/run_qemu.py $(BUILD)/$(VARIANT) \
		--qemu $(QEMU) --log $(BUILD)/$(VARIANT)-qemu.log \
		--csv $(BUILD)/$(VARIANT)-results.csv $(EXPECT)

clean:
	rm -rf $(addprefix $(BUILD)/,original fixed v6.1.1) build/presentation
	rm -f $(BUILD)/*-qemu.log $(BUILD)/*-results.csv

distclean: clean
	rm -rf $(BUILD)/venv $(TOOLS) $(TOOLS_NEWEST) $(BUILD)/qemu
