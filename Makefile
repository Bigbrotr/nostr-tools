# =====================================================
# 🚀 nostr-tools Makefile
# =====================================================
# Development automation and project management commands
# Run 'make help' for available commands
# =====================================================

.PHONY: help install install-dev install-ci test test-cov test-unit test-integration test-security test-performance \
        lint lint-fix format format-check clean build upload upload-test verify pre-commit \
        check check-all examples security-scan deps-check type-check docs-build docs-serve docs-clean version

# =====================================================
# Configuration Variables
# =====================================================

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

# =====================================================
# Default Target - Help Menu
# =====================================================

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
	@echo "  deps-check        Check for dependency updates"
	@echo ""
	@echo "$(BOLD)$(GREEN)🔍 Utilities:$(RESET)"
	@echo "  examples          Run example scripts"
	@echo "  verify            Verify installation"
	@echo ""
	@echo "$(BOLD)$(YELLOW)💡 Quick Start:$(RESET)"
	@echo "  make install-dev  # Set up development environment"
	@echo "  make check        # Run quality checks"
	@echo "  make test         # Run tests"

# =====================================================
# Installation targets
# =====================================================

install:
	@echo "$(BLUE)📦 Installing nostr-tools...$(RESET)"
	$(PYTHON) -m pip install .
	@echo "$(GREEN)✅ Installation complete!$(RESET)"

install-dev:
	@echo "$(BLUE)📦 Installing nostr-tools with development dependencies...$(RESET)"
	$(PYTHON) -m pip install -e ".[dev]"
	@echo "$(BLUE)🔧 Setting up pre-commit hooks...$(RESET)"
	pre-commit install
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

install-all:
	@echo "$(BLUE)📦 Installing nostr-tools with all optional dependencies...$(RESET)"
	$(PYTHON) -m pip install -e ".[all]"
	@echo "$(GREEN)✅ Full installation complete!$(RESET)"

install-ci:
	@echo "$(BLUE)📦 Installing for CI environment...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e ".[test,security]"
	@echo "$(GREEN)✅ CI environment ready!$(RESET)"

# =====================================================
# Code quality targets
# =====================================================

format:
	@echo "$(BLUE)🎨 Formatting code with Ruff...$(RESET)"
	$(PYTHON) -m ruff format $(SRC_DIRS) --exclude="src/nostr_tools/_version.py"
	@echo "$(GREEN)✅ Code formatted!$(RESET)"

format-check:
	@echo "$(BLUE)🎨 Checking code formatting...$(RESET)"
	$(PYTHON) -m ruff format --check $(SRC_DIRS) --exclude="src/nostr_tools/_version.py"

lint:
	@echo "$(BLUE)🔍 Running linting checks...$(RESET)"
	$(PYTHON) -m ruff check $(SRC_DIRS) --exclude="src/nostr_tools/_version.py"

lint-fix:
	@echo "$(BLUE)🔧 Running linting with fixes...$(RESET)"
	$(PYTHON) -m ruff check --fix $(SRC_DIRS) --exclude="src/nostr_tools/_version.py"
	@echo "$(GREEN)✅ Linting issues fixed!$(RESET)"

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
	@echo "$(GREEN)✅ Security scan complete!$(RESET)"

# =====================================================
# Testing targets
# =====================================================

test:
	@echo "$(BLUE)🧪 Running all tests...$(RESET)"
	$(PYTHON) -m pytest

test-unit:
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	$(PYTHON) -m pytest -m "not integration and not slow"

test-integration:
	@echo "$(BLUE)🧪 Running integration tests...$(RESET)"
	$(PYTHON) -m pytest -m integration

test-security:
	@echo "$(BLUE)🧪 Running security tests...$(RESET)"
	$(PYTHON) -m pytest -m security

test-performance:
	@echo "$(BLUE)🧪 Running performance benchmarks...$(RESET)"
	$(PYTHON) -m pytest -m benchmark --benchmark-only

test-cov:
	@echo "$(BLUE)🧪 Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest --cov=src/$(PACKAGE) --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/$(RESET)"

# =====================================================
# Build and distribution targets
# =====================================================

clean:
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	rm -rf build/ dist/ *.egg-info
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf .mypy_cache/ .ruff_cache/
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Cleanup complete!$(RESET)"

build: clean
	@echo "$(BLUE)📦 Building distribution packages...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)✅ Build complete! Packages in dist/$(RESET)"

upload: build
	@echo "$(BLUE)📤 Uploading to PyPI...$(RESET)"
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✅ Package uploaded to PyPI!$(RESET)"

upload-test: build
	@echo "$(BLUE)📤 Uploading to TestPyPI...$(RESET)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✅ Package uploaded to TestPyPI!$(RESET)"

# =====================================================
# Documentation targets
# =====================================================

docs-build:
	@echo "$(BLUE)📚 Building documentation...$(RESET)"
	cd docs && $(MAKE) html
	@echo "$(GREEN)✅ Documentation built in docs/_build/html/$(RESET)"

docs-serve: docs-build
	@echo "$(BLUE)📚 Serving documentation...$(RESET)"
	cd docs/_build/html && $(PYTHON) -m http.server

docs-clean:
	@echo "$(BLUE)🧹 Cleaning documentation build...$(RESET)"
	cd docs && $(MAKE) clean
	@echo "$(GREEN)✅ Documentation cleaned!$(RESET)"

# =====================================================
# Quality assurance targets
# =====================================================

check:
	@echo "$(BOLD)$(BLUE)🔍 Running quality checks...$(RESET)"
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) test-unit
	@echo "$(GREEN)✅ All quality checks passed!$(RESET)"

check-all:
	@echo "$(BOLD)$(BLUE)🔍 Running comprehensive quality checks...$(RESET)"
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) security-scan
	@$(MAKE) test-cov
	@echo "$(GREEN)✅ All comprehensive checks passed!$(RESET)"

pre-commit:
	@echo "$(BLUE)🪝 Running pre-commit hooks...$(RESET)"
	pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit checks complete!$(RESET)"

deps-check:
	@echo "$(BLUE)📦 Checking for dependency updates...$(RESET)"
	$(PYTHON) -m pip list --outdated
	@echo "$(YELLOW)💡 Run 'pip install --upgrade package-name' to update$(RESET)"

# =====================================================
# Utility targets
# =====================================================

version:
	@echo "$(BOLD)nostr-tools version: $(GREEN)$(VERSION)$(RESET)"

examples:
	@echo "$(BLUE)📝 Running example scripts...$(RESET)"
	@for example in examples/*.py; do \
		echo "$(YELLOW)Running $$example...$(RESET)"; \
		$(PYTHON) $$example || true; \
	done
	@echo "$(GREEN)✅ Examples complete!$(RESET)"

verify:
	@echo "$(BLUE)🔍 Verifying installation...$(RESET)"
	@$(PYTHON) -c "import $(PACKAGE); print(f'✅ {$(PACKAGE).__name__} v{$(PACKAGE).__version__} imported successfully')"
	@$(PYTHON) -c "from $(PACKAGE) import Event, Relay, Client; print('✅ Core classes imported successfully')"
	@echo "$(GREEN)✅ Installation verified!$(RESET)"

# =====================================================
# Development workflow helpers
# =====================================================

# Quick development cycle
dev: format lint-fix type-check test-unit
	@echo "$(GREEN)✅ Development cycle complete!$(RESET)"

# Release preparation
release-prep: clean check-all docs-build
	@echo "$(GREEN)✅ Release preparation complete!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Update CHANGELOG.md"
	@echo "  2. Commit changes"
	@echo "  3. Tag release: git tag v$(VERSION)"
	@echo "  4. Push tag: git push origin v$(VERSION)"

# =====================================================
# Special targets for project setup
# =====================================================

# Initialize new development environment
init: install-dev
	@echo "$(BLUE)🚀 Initializing development environment...$(RESET)"
	@mkdir -p tests examples docs
	@touch tests/__init__.py
	@echo "$(GREEN)✅ Project initialized!$(RESET)"

# Migrate from old project structure
migrate:
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
