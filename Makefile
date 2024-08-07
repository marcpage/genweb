.PHONY:clean venv test coverage lint format deploy
all:clean test coverage lint

MIN_TEST_COVERAGE=90
INITIAL_PYTHON?=python3
VENV_DIR?=.venv
LIBRARY=genweb
VENV_PYTHON?=$(VENV_DIR)/bin/python
VENV_PIP?=$(VENV_DIR)/bin/pip
SET_ENV?=. $(VENV_DIR)/bin/activate
SOURCES=$(shell find $(LIBRARY) -type f -iname "*.py")
TESTS=$(shell find tests -type f -iname "test_*.py")
FORMAT_FILE=$(VENV_DIR)/format.txt
LINT_FILE=$(VENV_DIR)/lint.txt
COVERAGE_FILE=.coverage
DEPLOY_FILE=$(VENV_DIR)/deploy.txt
PROJECT_FILE=pyproject.toml
SLEEP_TIME_IN_SECONDS=1
TEST_SERVER_TEST_DIR=test_published
PROD_SERVER_TEST_DIR=prod_published
BUILD_LOG=$(VENV_DIR)/build_log.txt
PIP_INSTALL=$(VENV_PIP) install --quiet --upgrade
PIP_INSTALL_TEST=pip install --no-cache-dir --quiet
SETTINGS_TOOL=devopsdriver.manage_settings

$(VENV_DIR)/touchfile: $(PROJECT_FILE)
	@test -d $(VENV_DIR) || $(INITIAL_PYTHON) -m venv $(VENV_DIR)
	@echo Ensuring pip is latest version
	@$(SET_ENV); $(PIP_INSTALL) pip
	@echo Fetching requirements
	@$(SET_ENV); $(PIP_INSTALL) .
	@touch $@

venv: $(VENV_DIR)/touchfile

$(COVERAGE_FILE): $(VENV_DIR)/touchfile $(SOURCES) $(TESTS)
	@$(SET_ENV); $(PIP_INSTALL) ".[test]"
	@$(SET_ENV); $(VENV_PYTHON) -m coverage run  --source $(LIBRARY) -m pytest

test: $(COVERAGE_FILE)

coverage: $(COVERAGE_FILE)
	@$(SET_ENV); $(VENV_PYTHON) -m coverage report -m --sort=cover --skip-covered --fail-under=$(MIN_TEST_COVERAGE)
	@if grep --quiet "test+coverage&message=$(MIN_TEST_COVERAGE)%" README.md; then true; else echo "Update README.md test coverage" && false; fi
	

$(FORMAT_FILE): $(VENV_DIR)/touchfile $(SOURCES)
	@$(SET_ENV); $(PIP_INSTALL) ".[dev]"
	@$(SET_ENV); $(VENV_PYTHON) -m black $(LIBRARY) &> $@

format: $(FORMAT_FILE)
	@cat $^

$(LINT_FILE): $(VENV_DIR)/touchfile $(SOURCES)
	@$(SET_ENV); $(PIP_INSTALL) ".[dev]"
	-@$(SET_ENV); $(VENV_PYTHON) -m pylint --disable cyclic-import $(LIBRARY) --output $@
	-@$(SET_ENV); $(VENV_PYTHON) -m black $(LIBRARY) --check >> $@  2>&1

lint: $(LINT_FILE)
	@cat $^
	@if grep --quiet "would be reformatted" $^; then echo "black failure!" && false; else true; fi
	@if grep --quiet "rated at 10.00/10" $^; then true; else echo "pylint failure!" && false; fi

clean:
	@rm -Rf $(VENV_DIR)
	@rm -f $(strip $(COVERAGE_FILE))*
	@rm -Rf `find . -type d -name __pycache__`
	@rm -Rf .pytest_cache
	@rm -Rf dist
	@rm -Rf build
	@rm -Rf *.egg-info
	@find . -iname "*.pyc" -delete
