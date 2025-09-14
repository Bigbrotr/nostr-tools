.PHONY: help install install-dev test lint format build clean upload check

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BOLD := \033[1m
RESET := \033[0m

# Project configuration
PYTHON := python3
PACKAGE := nostr_tools
SRC_DIR := src
TESTS_DIR := tests

# Get version from setuptools-scm
VERSION := $(shell $(PYTHON) -m setuptools_scm)

# Default target
help:
	@echo "$(BOLD)$(BLUE)🚀 nostr-tools Development Commands$(RESET)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📦 Setup & Installation:$(RESET)"
	@echo "  install           Install package in production mode"
	@echo "  install-dev       Install with development dependencies"
	@echo "  install-all       Install with all optional dependencies"
	@echo ""
	@echo "$(BOLD)$(GREEN)🎨 Code Quality:$(RESET)"
	@echo "  format            Format code with Ruff"
	@echo "  format-check      Check code formatting without changes"
	@echo "  lint              Run linting checks"
	@echo "  lint-fix          Run linting with automatic fixes"
	@echo "  type-check        Run MyPy type checking"
	@echo ""
	@echo "$(BOLD)$(GREEN)🧪 Testing:$(RESET)"
	@echo "  test              Run all tests"
	@echo "  test-unit         Run unit tests only"
	@echo "  test-integration  Run integration tests"
	@echo "  test-cov          Run tests with coverage report"
	@echo "  test-security     Run security checks"
	@echo ""
	@echo "$(BOLD)$(GREEN)🔧 Build & Distribution:$(RESET)"
	@echo "  build             Build distribution packages"
	@echo "  clean             Clean build artifacts"
	@echo "  upload            Upload to PyPI"
	@echo "  upload-test       Upload to TestPyPI"
	@echo ""
	@echo "$(BOLD)$(GREEN)✅ Quality Assurance:$(RESET)"
	@echo "  check             Run all checks (format, lint, type, test)"
	@echo "  pre-commit        Set up pre-commit hooks"

# Installation targets
install:
	@echo "$(BLUE)📦 Installing nostr-tools...$(RESET)"
	$(PYTHON) -m pip install .

install-dev:
	@echo "$(BLUE)📦 Installing nostr-tools with development dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[dev]

install-all:
	@echo "$(BLUE)📦 Installing nostr-tools with all dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[all]

# Code quality targets
format:
	@echo "$(BLUE)🎨 Formatting code...$(RESET)"
	$(PYTHON) -m ruff format $(SRC_DIR) $(TESTS_DIR) examples/

format-check:
	@echo "$(BLUE)🎨 Checking code formatting...$(RESET)"
	$(PYTHON) -m ruff format --check $(SRC_DIR) $(TESTS_DIR) examples/

lint:
	@echo "$(BLUE)🔍 Running linting checks...$(RESET)"
	$(PYTHON) -m ruff check $(SRC_DIR) $(TESTS_DIR) examples/

lint-fix:
	@echo "$(BLUE)🔧 Running linting with fixes...$(RESET)"
	$(PYTHON) -m ruff check --fix $(SRC_DIR) $(TESTS_DIR) examples/

type-check:
	@echo "$(BLUE)🏷️  Running type checks...$(RESET)"
	$(PYTHON) -m mypy $(SRC_DIR)

# Testing targets
test:
	@echo "$(BLUE)🧪 Running all tests...$(RESET)"
	$(PYTHON) -m pytest

test-unit:
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	$(PYTHON) -m pytest -m "unit or not integration"

test-integration:
	@echo "$(BLUE)🧪 Running integration tests...$(RESET)"
	$(PYTHON) -m pytest -m integration

test-cov:
	@echo "$(BLUE)🧪 Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=html --cov-report=term

test-security:
	@echo "$(BLUE)🔒 Running security checks...$(RESET)"
	$(PYTHON) -m bandit -r $(SRC_DIR)
	$(PYTHON) -m safety check
	$(PYTHON) -m pip-audit

# Build and distribution targets
build: clean
	@echo "$(BLUE)🔨 Building distribution packages...$(RESET)"
	$(PYTHON) -m build

clean:
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

upload: build
	@echo "$(BLUE)📤 Uploading to PyPI...$(RESET)"
	$(PYTHON) -m twine upload dist/*

upload-test: build
	@echo "$(BLUE)📤 Uploading to TestPyPI...$(RESET)"
	$(PYTHON) -m twine upload --repository testpypi dist/*

# Quality assurance targets
check: format-check lint type-check test-unit
	@echo "$(GREEN)✅ All checks passed!$(RESET)"

pre-commit:
	@echo "$(BLUE)🪝 Setting up pre-commit hooks...$(RESET)"
	$(PYTHON) -m pre_commit install

# Development utilities
dev-shell:
	@echo "$(BLUE)🐚 Starting development shell...$(RESET)"
	$(PYTHON) -i -c "import $(PACKAGE); print('$(PACKAGE) development shell ready')"

version:
	@echo "$(BLUE)📋 Current version: $(YELLOW)$(VERSION)$(RESET)"

deps-update:
	@echo "$(BLUE)🔄 Updating development dependencies...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip build twine
	$(PYTHON) -m pip install --upgrade -e .[all]

# CI/CD helpers
ci-install:
	@echo "$(BLUE)⚙️  Installing for CI...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[test]

ci-test:
	@echo "$(BLUE)🤖 Running CI tests...$(RESET)"
	$(PYTHON) -m pytest -v --tb=short

# Documentation (if using Sphinx)
docs:
	@echo "$(BLUE)📖 Building documentation...$(RESET)"
	@if [ -d "docs" ]; then \
		cd docs && $(PYTHON) -m sphinx . _build/html; \
	else \
		echo "$(YELLOW)No docs directory found$(RESET)"; \
	fi

docs-serve:
	@echo "$(BLUE)📖 Serving documentation...$(RESET)"
	@if [ -d "docs/_build/html" ]; then \
		$(PYTHON) -m http.server 8000 -d docs/_build/html; \
	else \
		echo "$(RED)Documentation not built. Run 'make docs' first$(RESET)"; \
	fi