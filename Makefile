.PHONY:clean venv test coverage lint format deploy
all:clean test coverage lint

MIN_TEST_COVERAGE=26
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

$(DEPLOY_FILE):$(LINT_FILE) $(COVERAGE_FILE) $(PROJECT_FILE) $(SOURCES) lint coverage
	@echo "Preparation cleanup"
	@rm -Rf dist build *.egg-info $(VENV_DIR)/$(TEST_SERVER_TEST_DIR) $(VENV_DIR)/$(PROD_SERVER_TEST_DIR)
	@echo "Validating version strings are correct"
	@$(SET_ENV); \
		VERSION=`python -c "print(__import__('devopsdriver').__version__)"`; \
		if grep --quiet "released&message=v$$VERSION&" README.md; then true; else echo "Update README.md badge version" && false; fi
	@$(SET_ENV); \
		VERSION=`python -c "print(__import__('devopsdriver').__version__)"`; \
		if grep --quiet "devopsdriver/$$VERSION/" README.md; then true; else echo "Update README.md PyPI version" && false; fi
	@echo "Putting tests in staging test dir: $(VENV_DIR)/$(TEST_SERVER_TEST_DIR)"
	@mkdir -p $(VENV_DIR)/$(TEST_SERVER_TEST_DIR)
	@cp -R tests $(VENV_DIR)/$(TEST_SERVER_TEST_DIR)/
	@echo "Putting tests in prod test dir: $(VENV_DIR)/$(PROD_SERVER_TEST_DIR)"
	@mkdir -p $(VENV_DIR)/$(PROD_SERVER_TEST_DIR)
	@cp -R tests $(VENV_DIR)/$(PROD_SERVER_TEST_DIR)/
	@echo "Installing tools"
	@$(SET_ENV); $(PIP_INSTALL) build twine
	@echo "Building package"
	@$(SET_ENV); $(VENV_PYTHON) -m build > $(BUILD_LOG)
	@echo "Uploading package to test server"
	@$(SET_ENV); \
		REPO=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_test.repo`; \
		USERNAME=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_test.username`; \
		PASSWORD=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_test.password`; \
		$(VENV_PYTHON) -m twine upload --repository $$REPO dist/* --username $$USERNAME --password $$PASSWORD
	@echo "Waiting for uploaded package to be avilable before testing"
	@sleep $(SLEEP_TIME_IN_SECONDS)
	@echo "First attempt at testing staging package"
	-@$(SET_ENV); \
		TESTURL=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_test.url`; \
		URL=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_prod.url`; \
		VERSION=`python -c "print(__import__('devopsdriver').__version__)"`; \
		cd $(VENV_DIR)/$(TEST_SERVER_TEST_DIR); \
		$(INITIAL_PYTHON) -m venv .venv; \
		$(SET_ENV); \
		$(PIP_INSTALL_TEST) --log $@ -i $$TESTURL  pytest $(LIBRARY)==$$VERSION --extra-index-url $$URL;
	@echo "Second attempt at testing staging package"
	@$(SET_ENV); \
		TESTURL=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_test.url`; \
		URL=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_prod.url`; \
		VERSION=`python -c "print(__import__('devopsdriver').__version__)"`; \
		cd $(VENV_DIR)/$(TEST_SERVER_TEST_DIR); \
		$(INITIAL_PYTHON) -m venv .venv; \
		$(SET_ENV); \
		$(PIP_INSTALL_TEST) --log $@ -i $$TESTURL  pytest $(LIBRARY)==$$VERSION --extra-index-url $$URL; \
		$(VENV_PYTHON) -m pytest
	@echo "Uploading package to production server"
	@$(SET_ENV); \
		REPO=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_prod.repo`; \
		USERNAME=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_prod.username`; \
		PASSWORD=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_prod.password`; \
		$(VENV_PYTHON) -m twine upload --repository $$REPO dist/* --username $$USERNAME --password $$PASSWORD
	@echo Waiting for uploaded package to be avilable before testing
	@sleep $(SLEEP_TIME_IN_SECONDS)
	@echo "First attempt at testing production package"
	-@$(SET_ENV); \
		URL=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_prod.url`; \
		VERSION=`python -c "print(__import__('devopsdriver').__version__)"`; \
		cd $(VENV_DIR)/$(PROD_SERVER_TEST_DIR); \
		$(INITIAL_PYTHON) -m venv .venv; \
		$(SET_ENV); \
		$(PIP_INSTALL_TEST) --log $@ -i $$URL pytest  $(LIBRARY)==$$VERSION;
	@echo "Second attempt at testing production package"
	@$(SET_ENV); \
		URL=`$(VENV_PYTHON) -m $(SETTINGS_TOOL) pypi_prod.url`; \
		VERSION=`python -c "print(__import__('devopsdriver').__version__)"`; \
		cd $(VENV_DIR)/$(PROD_SERVER_TEST_DIR); \
		$(INITIAL_PYTHON) -m venv .venv; \
		$(SET_ENV); \
		$(PIP_INSTALL_TEST) --log $@ -i $$URL pytest  $(LIBRARY)==$$VERSION; \
		$(VENV_PYTHON) -m pytest
	@touch $@

deploy: $(DEPLOY_FILE)

clean:
	@rm -Rf $(VENV_DIR)
	@rm -f $(strip $(COVERAGE_FILE))*
	@rm -Rf `find . -type d -name __pycache__`
	@rm -Rf .pytest_cache
	@rm -Rf dist
	@rm -Rf build
	@rm -Rf *.egg-info
	@find . -iname "*.pyc" -delete
