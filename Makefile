.PHONY: help install install-dev install-ci test test-cov test-unit test-integration test-security test-performance lint lint-fix format format-check clean build upload upload-test verify pre-commit check check-all examples security-scan deps-check type-check docs-build docs-serve docs-clean version

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
# Use src/ layout directories
SRC_DIRS := src/$(PACKAGE) tests examples
VERSION := $(shell $(PYTHON) -c "import setuptools_scm; print(setuptools_scm.get_version())" 2>/dev/null || echo "unknown")

# Default target
help:
	@echo "$(BOLD)$(BLUE)🚀 nostr-tools v$(VERSION) Development Commands$(RESET)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📦 Setup & Installation:$(RESET)"
	@echo "  install           Install package in production mode"
	@echo "  install-dev       Install with development dependencies"
	@echo "  install-all       Install with all optional dependencies"
	@echo "  install-ci        Install for CI environment"
	@echo ""
	@echo "$(BOLD)$(GREEN)🎨 Code Quality:$(RESET)"
	@echo "  format            Format code with Ruff"
	@echo "  format-check      Check code formatting without changes"
	@echo "  lint              Run linting checks"
	@echo "  lint-fix          Run linting with automatic fixes"
	@echo "  type-check        Run MyPy type checking"
	@echo "  security-scan     Run security checks (bandit, safety, pip-audit)"
	@echo ""
	@echo "$(BOLD)$(GREEN)🧪 Testing:$(RESET)"
	@echo "  test              Run all tests"
	@echo "  test-unit         Run unit tests only (fast)"
	@echo "  test-integration  Run integration tests (network required)"
	@echo "  test-security     Run security-focused tests"
	@echo "  test-performance  Run performance benchmarks"
	@echo "  test-cov          Run tests with coverage report"
	@echo ""
	@echo "$(BOLD)$(GREEN)🔧 Build & Distribution:$(RESET)"
	@echo "  build             Build distribution packages"
	@echo "  clean             Clean build artifacts"
	@echo "  upload            Upload to PyPI"
	@echo "  upload-test       Upload to TestPyPI"
	@echo "  version           Show current version"
	@echo ""
	@echo "$(BOLD)$(GREEN)📚 Documentation:$(RESET)"
	@echo "  docs-build        Build documentation"
	@echo "  docs-serve        Serve documentation locally"
	@echo "  docs-clean        Clean documentation build"
	@echo ""
	@echo "$(BOLD)$(GREEN)✅ Quality Assurance:$(RESET)"
	@echo "  check             Run all quality checks (fast)"
	@echo "  check-all         Run comprehensive quality checks"
	@echo "  pre-commit        Set up and run pre-commit hooks"

# =====================================================
# Installation targets
# =====================================================

install:
	@echo "$(BLUE)📦 Installing nostr-tools...$(RESET)"
	$(PYTHON) -m pip install .

install-dev:
	@echo "$(BLUE)📦 Installing nostr-tools with development dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[dev]

install-all:
	@echo "$(BLUE)📦 Installing nostr-tools with all dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[all]

install-ci:
	@echo "$(BLUE)📦 Installing for CI environment...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e .[test,security]

# =====================================================
# Code quality targets
# =====================================================

format:
	@echo "$(BLUE)🎨 Formatting code with Ruff...$(RESET)"
	$(PYTHON) -m ruff format $(SRC_DIRS)

format-check:
	@echo "$(BLUE)🎨 Checking code formatting...$(RESET)"
	$(PYTHON) -m ruff format --check $(SRC_DIRS)

lint:
	@echo "$(BLUE)🔍 Running linting checks...$(RESET)"
	$(PYTHON) -m ruff check $(SRC_DIRS)

lint-fix:
	@echo "$(BLUE)🔧 Running linting with fixes...$(RESET)"
	$(PYTHON) -m ruff check --fix $(SRC_DIRS)

type-check:
	@echo "$(BLUE)🏷️  Running type checks...$(RESET)"
	$(PYTHON) -m mypy src/$(PACKAGE)

security-scan:
	@echo "$(BLUE)🔒 Running security scans...$(RESET)"
	@echo "$(YELLOW)Running Bandit...$(RESET)"
	$(PYTHON) -m bandit -r src/$(PACKAGE) -f json -o bandit-report.json || true
	$(PYTHON) -m bandit -r src/$(PACKAGE)
	@echo "$(YELLOW)Running Safety...$(RESET)"
	$(PYTHON) -m safety check
	@echo "$(YELLOW)Running pip-audit...$(RESET)"
	$(PYTHON) -m pip_audit

# =====================================================
# Testing targets
# =====================================================

test:
	@echo "$(BLUE)🧪 Running all tests...$(RESET)"
	$(PYTHON) -m pytest

test-unit:
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	$(PYTHON) -m pytest -m "unit or (not integration and not slow)"

test-integration:
	@echo "$(BLUE)🧪 Running integration tests...$(RESET)"
	$(PYTHON) -m pytest -m integration

test-security:
	@echo "$(BLUE)🧪 Running security tests...$(RESET)"
	$(PYTHON) -m pytest -m security

test-performance:
	@echo "$(BLUE)🧪 Running performance tests...$(RESET)"
	$(PYTHON) -m pytest -m "not (unit or integration)" --benchmark-only

test-cov:
	@echo "$(BLUE)🧪 Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest --cov=src/$(PACKAGE) --cov-report=html --cov-report=term --cov-report=xml

# =====================================================
# Build and distribution targets
# =====================================================

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
	rm -rf bandit-report.json
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	@echo "$(BLUE)🔨 Building distribution packages...$(RESET)"
	$(PYTHON) -m build

version:
	@echo "$(BLUE)📋 Current version: $(YELLOW)$(VERSION)$(RESET)"

upload: build
	@echo "$(BLUE)📤 Uploading to PyPI...$(RESET)"
	$(PYTHON) -m twine upload dist/*

upload-test: build
	@echo "$(BLUE)📤 Uploading to TestPyPI...$(RESET)"
	$(PYTHON) -m twine upload --repository testpypi dist/*

# =====================================================
# Documentation targets
# =====================================================

docs-build:
	@echo "$(BLUE)📖 Building documentation...$(RESET)"
	@if [ -d "docs" ]; then \
		cd docs && $(PYTHON) -m sphinx . _build/html; \
	else \
		echo "$(YELLOW)No docs directory found$(RESET)"; \
	fi

docs-serve:
	@echo "$(BLUE)📖 Serving documentation at http://localhost:8000...$(RESET)"
	@if [ -d "docs/_build/html" ]; then \
		$(PYTHON) -m http.server 8000 -d docs/_build/html; \
	else \
		echo "$(RED)Documentation not built. Run 'make docs-build' first$(RESET)"; \
	fi

docs-clean:
	@echo "$(BLUE)🧹 Cleaning documentation build...$(RESET)"
	@if [ -d "docs/_build" ]; then \
		rm -rf docs/_build/; \
	fi

# =====================================================
# Quality assurance targets
# =====================================================

check: format-check lint type-check test-unit
	@echo "$(GREEN)✅ All fast quality checks passed!$(RESET)"

check-all: format-check lint type-check security-scan test
	@echo "$(GREEN)✅ All quality checks passed!$(RESET)"

pre-commit:
	@echo "$(BLUE)🪝 Setting up pre-commit hooks...$(RESET)"
	$(PYTHON) -m pre_commit install
	$(PYTHON) -m pre_commit run --all-files

# =====================================================
# Development utilities
# =====================================================

deps-update:
	@echo "$(BLUE)🔄 Updating development dependencies...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip build twine setuptools-scm
	$(PYTHON) -m pip install --upgrade -e .[all]

dev-shell:
	@echo "$(BLUE)🐚 Starting development shell...$(RESET)"
	$(PYTHON) -i -c "import sys; sys.path.insert(0, 'src'); import $(PACKAGE); print('$(PACKAGE) development shell ready - version $(VERSION)')"

examples:
	@echo "$(BLUE)🎯 Running examples...$(RESET)"
	@for example in examples/*.py; do \
		if [ -f "$$example" ]; then \
			echo "$(YELLOW)Running $$example...$(RESET)"; \
			$(PYTHON) "$$example" || echo "$(RED)Example $$example failed$(RESET)"; \
		fi; \
	done

# =====================================================
# CI/CD helpers
# =====================================================

ci-test:
	@echo "$(BLUE)🤖 Running CI test suite...$(RESET)"
	$(PYTHON) -m pytest -v --tb=short --maxfail=3

ci-check:
	@echo "$(BLUE)🤖 Running CI quality checks...$(RESET)"
	$(PYTHON) -m ruff check $(SRC_DIRS)
	$(PYTHON) -m ruff format --check $(SRC_DIRS)
	$(PYTHON) -m mypy src/$(PACKAGE)

# =====================================================
# Migration helpers (temporary)
# =====================================================

migrate-to-src:
	@echo "$(BLUE)🔄 Migrating to src/ layout...$(RESET)"
	@if [ -d "$(PACKAGE)" ] && [ ! -d "src/$(PACKAGE)" ]; then \
		echo "Creating src/ directory..."; \
		mkdir -p src; \
		echo "Moving $(PACKAGE)/ to src/$(PACKAGE)/..."; \
		mv $(PACKAGE) src/; \
		echo "Creating py.typed marker..."; \
		touch src/$(PACKAGE)/py.typed; \
		echo "$(GREEN)✅ Migration completed! Update your pyproject.toml and reinstall.$(RESET)"; \
	else \
		echo "$(YELLOW)Migration already completed or $(PACKAGE) directory not found$(RESET)"; \
	fi

# =====================================================
# Debugging and development helpers
# =====================================================

debug-info:
	@echo "$(BOLD)$(BLUE)🔍 Debug Information$(RESET)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PYTHON) -m pip --version)"
	@echo "Project root: $(shell pwd)"
	@echo "Package version: $(VERSION)"
	@echo "Package location: $(shell $(PYTHON) -c 'import $(PACKAGE); print($(PACKAGE).__file__)' 2>/dev/null || echo 'Not installed')"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "Git status: $(shell git status --porcelain 2>/dev/null | wc -l || echo 'N/A') modified files"

list-deps:
	@echo "$(BLUE)📋 Listing current dependencies...$(RESET)"
	$(PYTHON) -m pip list

freeze-deps:
	@echo "$(BLUE)🧊 Freezing current dependencies...$(RESET)"
	$(PYTHON) -m pip freeze > requirements-frozen.txt
	@echo "$(GREEN)Dependencies frozen to requirements-frozen.txt$(RESET)"

# Verification that installation worked correctly
verify-install:
	@echo "$(BLUE)🔍 Verifying installation...$(RESET)"
	$(PYTHON) -c "import $(PACKAGE); print(f'✅ {$(PACKAGE).__name__} v{$(PACKAGE).__version__} imported successfully')"
	$(PYTHON) -c "from $(PACKAGE) import Event, Relay, Client; print('✅ Core classes imported successfully')"
	@echo "$(GREEN)✅ Installation verified successfully!$(RESET)"