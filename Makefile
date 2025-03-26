### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Python checks
UV?=uv

# installed?
ifeq (, $(shell which $(UV) ))
  $(error "UV=$(UV) not found in $(PATH)")
endif


BACKEND_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
GIT_FOLDER=$(BACKEND_FOLDER)/.git
VENV_FOLDER=$(BACKEND_FOLDER)/.venv
BIN_FOLDER=$(VENV_FOLDER)/bin


all: help

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

############################################
# Installation
############################################
.PHONY: clean
clean: ## Clean environment
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	rm -rf $(VENV_FOLDER) .python-version .ruff_cache .pytest_cache uv.lock

$(VENV_FOLDER): ## Install dependencies
	@echo "$(GREEN)==> Install environment$(RESET)"
	@uv sync

.PHONY: install
install: $(VENV_FOLDER) ## Install the project
	if [ -d $(GIT_FOLDER) ]; then hatch run pre-commit install; else echo "$(RED) Not installing pre-commit$(RESET)";fi

############################################
# QA
############################################
.PHONY: lint
lint: $(VENV_FOLDER) ## Check code base according to our standards
	@echo "$(GREEN)==> Lint codebase$(RESET)"
	@uv run pre-commit run -a

.PHONY: format
format: $(VENV_FOLDER) ## Fix code base according to our standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	@uv run pre-commit run -a

############################################
# Tests
############################################
.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest

.PHONY: test-coverage
test-coverage: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest

############################################
# Release
############################################
.PHONY: changelog
changelog: ## Release the package to pypi.org
	@echo "🚀 Display the draft for the changelog"
	@uv run towncrier --draft

.PHONY: release
release: ## Release the package to pypi.org
	@echo "🚀 Release package"
	@uv run prerelease
	@uv run release
	@rm -Rf dist
	@uv build
	@uv publish
	@uv run postrelease
