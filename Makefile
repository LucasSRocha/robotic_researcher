.PHONY: help
help:  ## Display this help
	@printf "\nHelp documentation for this project\n"
	@printf "\nUsage:\n  make [command] \n\n"
	@printf "Commands:\n"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean: clean-eggs clean-build  ## Clean bloat files from project
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '_pycache_' -delete
	@find . -type d -name "__pycache__" -exec rm -r {} +

clean-eggs:  ## Remove egg files
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/

clean-build:  ## Clean build files
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

set-path:  ## Set Python Path
    export PYTHONPATH=.

###
# Dependencies section
###
.PHONY: _base_pip
_base_pip:
	@pip install -U pip poetry

.PHONY: dev-dependencies
dev-dependencies: _base_pip  ## Install dev and main dependencies
	@poetry install --no-root

.PHONY: dependencies
dependencies: _base_pip ## Install dependencies
	@poetry install --no-root --only main

.PHONY: ci-dependencies
ci-dependencies: _base_pip  ## Install dependencies using pip
	@poetry export --without-hashes --with dev -f requirements.txt > requirements.txt
	@pip install -r requirements.txt

.PHONY: outdated
outdated: ## Show outdated packages
	@poetry show --outdated


###
# Lint section
###
_flake8:
	@flake8 .

_black:
	@black --check .

_isort:
	@isort --diff --check-only .

_isort-fix:
	@isort .

_black_fix:
	@black .

.PHONY: lint
lint: _flake8 _isort _black   ## Check code lint

.PHONY: format-code
format-code: _isort-fix _black_fix  ## Format code

###
# Tests section
###
.PHONY: test
test: ## Run tests
	@poetry run pytest

.PHONY: test-unit
test-unit:  ## Run unit tests
	@poetry run pytest -m "not integration"

.PHONY: test-coverage
test-coverage-unit: clean ## Run unit tests with coverage output
	@poetry run pytest -m "not integration" . --cov . --cov-report term-missing --cov-report xml --cov-report html

.PHONY: test-coverage
test-coverage: clean ## Run tests with coverage output
	@poetry run pytest . --cov . --cov-report term-missing --cov-report xml --cov-report html

.PHONY: test-debug
test-debug: clean ## Run tests with active pdb
	@poetry run pytest --pdb
