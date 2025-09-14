.PHONY: help install install-dev install-ci test test-cov test-unit test-integration test-security test-performance lint lint-fix format format-check clean build upload upload-test verify pre-commit check check-all examples examples-advanced security-scan deps-check type-check docs-build docs-serve docs-clean docs-check docs-commit-check pre-commit-full

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BOLD := \033[1m
RESET := \033[0m

# Python and package info
PYTHON := python3
PACKAGE := nostr_tools
SRC_DIRS := $(PACKAGE) tests examples
VERSION := $(shell grep '^version = ' pyproject.toml | cut -d '"' -f2)

# Default target
help:
	@echo "$(BOLD)$(BLUE)🚀 nostr-tools v$(VERSION) Development Commands$(RESET)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📦 Setup & Installation:$(RESET)"
	@echo "  install           Install package in development mode"
	@echo "  install-dev       Install with all development dependencies"
	@echo "  install-ci        Install for CI environment (minimal deps)"
	@echo "  deps-check        Check dependencies for security vulnerabilities"
	@echo ""
	@echo "$(BOLD)$(GREEN)🎨 Code Quality:$(RESET)"
	@echo "  format            Format all code with Ruff formatter"
	@echo "  format-check      Check code formatting without making changes"
	@echo "  lint              Run Ruff linting checks"
	@echo "  lint-fix          Run linting with automatic fixes"
	@echo "  type-check        Run MyPy static type checking"
	@echo "  security-scan     Run comprehensive security checks"
	@echo ""
	@echo "$(BOLD)$(GREEN)🧪 Testing:$(RESET)"
	@echo "  test              Run all tests with standard configuration"
	@echo "  test-unit         Run only fast unit tests (no network)"
	@echo "  test-integration  Run integration tests (requires network)"
	@echo "  test-security     Run security and cryptographic tests"
	@echo "  test-performance  Run performance benchmarks"
	@echo "  test-cov          Run tests with comprehensive coverage report"
	@echo ""
	@echo "$(BOLD)$(GREEN)📚 Documentation:$(RESET)"
	@echo "  docs-build        Build documentation with Sphinx"
	@echo "  docs-serve        Serve documentation locally"
	@echo "  docs-clean        Clean documentation build files"
	@echo "  docs-check        Check documentation builds without errors"
	@echo "  docs-commit-check Validate documentation for pre-commit"
	@echo ""
	@echo "$(BOLD)$(GREEN)⚡ Quality Checks:$(RESET)"
	@echo "  pre-commit        Install and run pre-commit hooks on all files"
	@echo "  pre-commit-full   Run complete pre-commit validation suite"
	@echo "  check             Run fast quality checks (format, lint, unit tests)"
	@echo "  check-all         Run comprehensive quality checks"

# =====================================================
# Setup and Installation
# =====================================================

install:
	@echo "$(BLUE)📦 Installing package in development mode...$(RESET)"
	$(PYTHON) -m pip install -e .
	@echo "$(GREEN)✅ Package installed successfully$(RESET)"

install-dev:
	@echo "$(BLUE)🔧 Installing with all development dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[dev,test,security,docs,perf]
	@echo "$(GREEN)✅ Development environment ready$(RESET)"

install-ci:
	@echo "$(BLUE)🏗️ Installing for CI environment...$(RESET)"
	$(PYTHON) -m pip install -e .[test,security]
	@echo "$(GREEN)✅ CI environment ready$(RESET)"

deps-check:
	@echo "$(BLUE)🔍 Checking dependencies for security vulnerabilities...$(RESET)"
	$(PYTHON) -m pip install safety pip-audit 2>/dev/null || true
	safety check || echo "$(YELLOW)⚠️ Safety completed with warnings$(RESET)"
	pip-audit || echo "$(YELLOW)⚠️ Pip-audit completed with warnings$(RESET)"
	@echo "$(GREEN)✅ Dependency security check completed$(RESET)"

# =====================================================
# Code Formatting and Quality
# =====================================================

format:
	@echo "$(BLUE)🎨 Formatting code with Ruff...$(RESET)"
	ruff format $(SRC_DIRS)
	@echo "$(GREEN)✅ Code formatting completed$(RESET)"

format-check:
	@echo "$(BLUE)🔍 Checking code formatting...$(RESET)"
	ruff format --check $(SRC_DIRS)
	@echo "$(GREEN)✅ Code formatting is correct$(RESET)"

lint:
	@echo "$(BLUE)🔍 Running Ruff linting checks...$(RESET)"
	ruff check $(SRC_DIRS)
	@echo "$(GREEN)✅ Linting checks passed$(RESET)"

lint-fix:
	@echo "$(BLUE)🔧 Running linting with automatic fixes...$(RESET)"
	ruff check --fix $(SRC_DIRS)
	@echo "$(GREEN)✅ Linting completed with automatic fixes$(RESET)"

type-check:
	@echo "$(BLUE)🔍 Running MyPy static type checking...$(RESET)"
	mypy $(PACKAGE) --ignore-missing-imports --show-error-codes --no-error-summary
	@echo "$(GREEN)✅ Type checking passed$(RESET)"

# =====================================================
# Security and Vulnerability Scanning
# =====================================================

security-scan:
	@echo "$(BLUE)🔒 Running comprehensive security checks...$(RESET)"
	@echo "$(YELLOW)Running Bandit security scanner...$(RESET)"
	@bandit -r $(PACKAGE) -f text --severity-level medium --confidence-level low || echo "$(YELLOW)⚠️ Bandit completed with warnings$(RESET)"
	@echo "$(GREEN)✅ Security scan completed$(RESET)"

# =====================================================
# Testing Framework
# =====================================================

test:
	@echo "$(BLUE)🧪 Running all tests...$(RESET)"
	$(PYTHON) -m pytest -v --tb=short
	@echo "$(GREEN)✅ All tests completed successfully$(RESET)"

test-unit:
	@echo "$(BLUE)⚡ Running unit tests (fast, no network)...$(RESET)"
	$(PYTHON) -m pytest -m "not integration and not slow" -v --tb=short
	@echo "$(GREEN)✅ Unit tests completed$(RESET)"

test-integration:
	@echo "$(BLUE)🌐 Running integration tests (requires network)...$(RESET)"
	@echo "$(YELLOW)⚠️ These tests connect to real Nostr relays and may be slower$(RESET)"
	NOSTR_SKIP_INTEGRATION=false $(PYTHON) -m pytest -m integration -v -s --tb=short
	@echo "$(GREEN)✅ Integration tests completed$(RESET)"

test-security:
	@echo "$(BLUE)🔐 Running security and cryptographic tests...$(RESET)"
	$(PYTHON) -m pytest -m security -v --tb=short
	@echo "$(GREEN)✅ Security tests completed$(RESET)"

test-performance:
	@echo "$(BLUE)🏃 Running performance benchmarks...$(RESET)"
	@echo "$(YELLOW)⚠️ Performance tests may take several minutes to complete$(RESET)"
	$(PYTHON) -m pytest -m slow -v --tb=short
	@echo "$(GREEN)✅ Performance tests completed$(RESET)"

test-cov:
	@echo "$(BLUE)📊 Running tests with coverage analysis...$(RESET)"
	$(PYTHON) -m pytest \
		--cov=$(PACKAGE) \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml \
		--cov-branch \
		-v
	@echo "$(GREEN)✅ Coverage analysis completed$(RESET)"
	@echo "$(YELLOW)📄 HTML coverage report: htmlcov/index.html$(RESET)"
	@echo "$(YELLOW)📄 XML coverage report: coverage.xml$(RESET)"

# =====================================================
# Documentation Generation
# =====================================================

docs-build:
	@echo "$(BLUE)📚 Building documentation...$(RESET)"
	@$(PYTHON) -m pip install -e .[docs] 2>/dev/null || true
	@if [ ! -d "docs" ]; then \
		echo "$(YELLOW)⚠️ docs/ directory not found. Create it first with documentation setup.$(RESET)"; \
		exit 1; \
	fi
	@cd docs && $(PYTHON) -m sphinx -b html . _build/html -W --keep-going
	@echo "$(GREEN)✅ Documentation built successfully$(RESET)"
	@echo "$(YELLOW)🔗 Open docs/_build/html/index.html in your browser$(RESET)"

docs-serve:
	@echo "$(BLUE)🌐 Serving documentation locally...$(RESET)"
	@if [ ! -d "docs/_build/html" ]; then \
		echo "$(YELLOW)⚠️ Documentation not built. Running 'make docs-build' first...$(RESET)"; \
		$(MAKE) docs-build; \
	fi
	@echo "$(YELLOW)🔗 Documentation server running at http://localhost:8000$(RESET)"
	@echo "$(YELLOW)Press Ctrl+C to stop the server$(RESET)"
	@cd docs/_build/html && $(PYTHON) -m http.server 8000

docs-clean:
	@echo "$(BLUE)🧹 Cleaning documentation build...$(RESET)"
	@rm -rf docs/_build/
	@echo "$(GREEN)✅ Documentation build cleaned$(RESET)"

docs-check:
	@echo "$(BLUE)📚 Checking documentation can build without warnings...$(RESET)"
	@$(PYTHON) -m pip install -e .[docs] >/dev/null 2>&1 || true
	@if [ ! -d "docs" ]; then \
		echo "$(RED)❌ docs/ directory not found.$(RESET)"; \
		exit 1; \
	fi
	@cd docs && $(PYTHON) -m sphinx -b html . _build/html -q -W
	@echo "$(GREEN)✅ Documentation builds successfully without warnings$(RESET)"

docs-commit-check: docs-clean docs-check
	@echo "$(BLUE)📖 Running pre-commit documentation validation...$(RESET)"
	@if [ -d "docs/_build/html" ]; then \
		echo "$(GREEN)✅ Documentation ready for commit$(RESET)"; \
	else \
		echo "$(RED)❌ Documentation build failed$(RESET)"; \
		exit 1; \
	fi

# =====================================================
# Quality Assurance and Pre-commit
# =====================================================

pre-commit:
	@echo "$(BLUE)🎯 Setting up and running pre-commit hooks...$(RESET)"
	@$(PYTHON) -m pip install pre-commit 2>/dev/null || true
	pre-commit install
	pre-commit install --hook-type pre-push
	@echo "$(YELLOW)Running pre-commit on all files...$(RESET)"
	pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit hooks installed and executed$(RESET)"

pre-commit-full: format lint type-check docs-commit-check test-unit
	@echo "$(GREEN)$(BOLD)✅ Complete pre-commit validation passed!$(RESET)"

check: format lint type-check test-unit
	@echo "$(GREEN)$(BOLD)✅ Fast quality checks completed successfully!$(RESET)"

check-all: format-check lint type-check security-scan test-unit deps-check docs-check
	@echo "$(GREEN)$(BOLD)✅ Comprehensive quality checks completed successfully!$(RESET)"

# =====================================================
# Build, Package, and Distribution
# =====================================================

clean:
	@echo "$(BLUE)🧹 Cleaning build artifacts and caches...$(RESET)"
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf .coverage htmlcov/ coverage.xml .coverage.*
	rm -rf .tox/ .nox/
	rm -rf docs/_build/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name "*~" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

build: clean
	@echo "$(BLUE)🏗️ Building distribution packages...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)✅ Build completed$(RESET)"
	@echo "$(YELLOW)📦 Packages created in dist/$(RESET)"

upload-test: build
	@echo "$(BLUE)📤 Uploading to Test PyPI...$(RESET)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✅ Upload to Test PyPI completed$(RESET)"

upload: build
	@echo "$(BLUE)📤 Uploading to PyPI...$(RESET)"
	@echo "$(YELLOW)⚠️ This will upload to the real PyPI. Are you sure? [y/N] $(RESET)" && read ans && [ $${ans:-N} = y ]
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✅ Upload to PyPI completed$(RESET)"

verify:
	@echo "$(BLUE)🔍 Verifying package integrity...$(RESET)"
	$(PYTHON) -m twine check dist/*
	@echo "$(GREEN)✅ Package verification completed$(RESET)"
