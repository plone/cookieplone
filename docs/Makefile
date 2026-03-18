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

CURRENT_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ROOT_FOLDER=$(CURRENT_FOLDER)/../
VENV_FOLDER=$(ROOT_FOLDER)/.venv

# Makefile for Sphinx documentation
.DEFAULT_GOAL   = help
SHELL           = bash

# You can set these variables from the command line.
SPHINXOPTS      ?=
PAPER           ?= a4

# Internal variables.
GREEN=`tput setaf 2`
RESET=`tput sgr0`
SPHINXBUILD     = "$(realpath .venv/bin/sphinx-build)"
DOCS_DIR        = $(CURRENT_FOLDER)/src/
BUILDDIR        = $(CURRENT_FOLDER)/_build
PAPEROPT_a4     = -D latex_elements.papersize=a4
PAPEROPT_letter = -D latex_elements.papersize=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) $(DOCS_DIR)
VALEFILES       := $(shell find $(DOCS_DIR) -type f -name "*.md" -print)
VALEOPTS        ?=
PYTHONVERSION   = >=3.11,<3.14

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help:  # This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# environment management
.PHONY: clean
clean:  ## Clean docs build directory
	@rm -rf $(BUILDDIR)/
# /environment management


# documentation builders
.PHONY: html
html: $(VENV_FOLDER)  ## Build html
	@uv run sphinx-build -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: livehtml
livehtml: $(VENV_FOLDER)  ## Rebuild Sphinx documentation on changes, with live-reload in the browser
	@uv run sphinx-autobuild \
		--ignore "*.swp" \
		--port 8050 \
		-b html $(DOCS_DIR) "$(BUILDDIR)/html" $(SPHINXOPTS)

.PHONY: dirhtml
dirhtml: $(VENV_FOLDER)
	@uv run sphinx-build -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

.PHONY: singlehtml
singlehtml: $(VENV_FOLDER)
	@uv run sphinx-build -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

.PHONY: text
text: $(VENV_FOLDER)
	@uv run sphinx-build -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

.PHONY: changes
changes: $(VENV_FOLDER)
	@uv run sphinx-build -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

.PHONY: build
build: html  ## Build documentation in HTML format

# /documentation builders


# test
.PHONY: linkcheck
linkcheck: $(VENV_FOLDER)  ## Run linkcheck
	@uv run sphinx-build -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: linkcheckbroken
linkcheckbroken: $(VENV_FOLDER)  ## Run linkcheck and show only broken links
	@uv run sphinx-build -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck | GREP_COLORS='0;31' grep -wi "broken\|redirect" --color=always | GREP_COLORS='0;31' grep -vi "https://github.com/plone/cookieplone/issues/" --color=always && if test $$? = 0; then exit 1; fi || test $$? = 1
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: doctest
doctest: $(VENV_FOLDER)  ## Test snippets in the documentation
	@uv run sphinx-build -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest/output.txt."

.PHONY: vale
vale: $(VENV_FOLDER)  ## Run Vale style, grammar, and spell checks
	@uv run vale sync
	@uv run vale --no-wrap $(VALEOPTS) $(VALEFILES)
	@echo "Vale is finished; look for any errors in the above output."
	@echo

.PHONY: test
test: clean vale linkcheckbroken doctest  ## Clean docs build, then run vale, linkcheckbroken, and doctest

.PHONY: all
all: clean vale linkcheckbroken html  ## Clean docs build, then run linkcheckbroken, and build html
# /test
