# =====================================================
# 🚀 nostr-tools Makefile
# =====================================================
# Professional development automation and project management
# Run 'make help' for available commands
# =====================================================

.PHONY: help install install-dev install-ci clean clean-all \
        format format-check lint lint-fix type-check \
        test test-unit test-cov test-watch test-quick \
        security security-bandit security-safety security-audit \
        docs docs-build docs-serve docs-clean docs-check docs-open \
        build build-check dist-check publish publish-test \
        pre-commit check check-ci check-all verify-all \
        version info deps-update

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
SRC_DIRS := src/$(PACKAGE)
TEST_DIRS := tests
DOCS_DIR := docs
DOCS_BUILD := $(DOCS_DIR)/_build
DIST_DIR := dist
BUILD_DIR := build

# Get version from git tags
VERSION := $(shell $(PYTHON) -c "import setuptools_scm; print(setuptools_scm.get_version())" 2>/dev/null || echo "unknown")

# Security scan configuration (centralized)
BANDIT_FLAGS := -r $(SRC_DIRS) -f json -o bandit-report.json
SECURITY_IGNORE := GHSA-4xh5-x5gv-qwph PYSEC-2022-42991 GHSA-xqrq-4mgf-ff32
PIP_AUDIT_FLAGS := --ignore-vuln $(SECURITY_IGNORE) --skip-editable

# =====================================================
# Help and Information
# =====================================================

help:
	@echo "$(BOLD)$(BLUE)🚀 nostr-tools v$(VERSION) - Development Commands$(RESET)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📦 Setup & Installation:$(RESET)"
	@echo "  install           Install package in production mode"
	@echo "  install-dev       Install with all development dependencies"
	@echo "  install-ci        Install for CI environment (test dependencies only)"
	@echo ""
	@echo "$(BOLD)$(GREEN)🎨 Code Quality:$(RESET)"
	@echo "  format            Format code with Ruff (auto-fix)"
	@echo "  format-check      Check formatting without making changes"
	@echo "  lint              Run all linters (Ruff + MyPy)"
	@echo "  lint-fix          Run linters with auto-fix"
	@echo "  type-check        Run MyPy static type checking"
	@echo ""
	@echo "$(BOLD)$(GREEN)🔒 Security:$(RESET)"
	@echo "  security          Run all security scans (bandit + safety + pip-audit)"
	@echo "  security-bandit   Run Bandit security linter"
	@echo "  security-safety   Run Safety dependency vulnerability scan"
	@echo "  security-audit    Run pip-audit for package vulnerabilities"
	@echo ""
	@echo "$(BOLD)$(GREEN)🧪 Testing:$(RESET)"
	@echo "  test              Run all tests with coverage"
	@echo "  test-unit         Run unit tests only (fast)"
	@echo "  test-cov          Run tests and generate HTML coverage report"
	@echo "  test-quick        Quick test run without coverage"
	@echo "  test-watch        Run tests in watch mode (re-run on changes)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📚 Documentation:$(RESET)"
	@echo "  docs-build        Build documentation"
	@echo "  docs-serve        Build and serve documentation locally"
	@echo "  docs-clean        Clean documentation build files"
	@echo "  docs-check        Build docs and verify (used in CI)"
	@echo "  docs-open         Build and open documentation in browser"
	@echo ""
	@echo "$(BOLD)$(GREEN)📦 Build & Release:$(RESET)"
	@echo "  build             Build source and wheel distributions"
	@echo "  build-check       Build and verify package integrity"
	@echo "  dist-check        Verify distribution packages with twine"
	@echo "  publish-test      Upload to Test PyPI"
	@echo "  publish           Upload to production PyPI"
	@echo ""
	@echo "$(BOLD)$(GREEN)✅ Quality Assurance:$(RESET)"
	@echo "  pre-commit        Run pre-commit hooks on all files"
	@echo "  check             Run all quality checks (format + lint + type)"
	@echo "  check-ci          Run all CI checks (check + security + test)"
	@echo "  check-all         Run comprehensive checks (check-ci + docs + build)"
	@echo "  verify-all        Full verification before release"
	@echo ""
	@echo "$(BOLD)$(GREEN)🛠️  Utilities:$(RESET)"
	@echo "  clean             Remove build artifacts and cache"
	@echo "  clean-all         Deep clean (including venv, docs, coverage)"
	@echo "  version           Show current version"
	@echo "  info              Show project information"
	@echo "  deps-update       Update pre-commit hooks"
	@echo ""

version:
	@echo "$(BOLD)$(BLUE)📌 Version:$(RESET) $(VERSION)"

info:
	@echo "$(BOLD)$(BLUE)📊 Project Information$(RESET)"
	@echo "$(BOLD)Name:$(RESET) nostr-tools"
	@echo "$(BOLD)Version:$(RESET) $(VERSION)"
	@echo "$(BOLD)Python:$(RESET) $(shell $(PYTHON) --version)"
	@echo "$(BOLD)Package:$(RESET) $(PACKAGE)"
	@echo "$(BOLD)Source:$(RESET) $(SRC_DIRS)"
	@echo "$(BOLD)Tests:$(RESET) $(TEST_DIRS)"

# =====================================================
# Installation and Setup
# =====================================================

install:
	@echo "$(BLUE)📦 Installing package...$(RESET)"
	$(PYTHON) -m pip install -e .
	@echo "$(GREEN)✅ Installation complete!$(RESET)"

install-dev:
	@echo "$(BLUE)📦 Installing development dependencies...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e ".[dev]"
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"
	@echo "$(YELLOW)💡 Run 'make pre-commit' to set up git hooks$(RESET)"

install-ci:
	@echo "$(BLUE)📦 Installing CI dependencies...$(RESET)"
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	@echo "$(GREEN)✅ CI environment ready!$(RESET)"

# =====================================================
# Code Quality
# =====================================================

format:
	@echo "$(BLUE)🎨 Formatting code with Ruff...$(RESET)"
	$(PYTHON) -m ruff format $(SRC_DIRS) $(TEST_DIRS) examples
	@echo "$(GREEN)✅ Code formatted!$(RESET)"

format-check:
	@echo "$(BLUE)🔍 Checking code formatting...$(RESET)"
	$(PYTHON) -m ruff format --check $(SRC_DIRS) $(TEST_DIRS) examples --exclude="src/nostr_tools/_version.py"
	@echo "$(GREEN)✅ Formatting check passed!$(RESET)"

lint:
	@echo "$(BLUE)🔍 Running linters...$(RESET)"
	@echo "$(YELLOW)Running Ruff linter...$(RESET)"
	$(PYTHON) -m ruff check $(SRC_DIRS) $(TEST_DIRS) examples
	@echo "$(YELLOW)Running MyPy type checker...$(RESET)"
	$(PYTHON) -m mypy $(SRC_DIRS) --show-error-codes
	@echo "$(GREEN)✅ All linters passed!$(RESET)"

lint-fix:
	@echo "$(BLUE)🔧 Running linters with auto-fix...$(RESET)"
	$(PYTHON) -m ruff check --fix $(SRC_DIRS) $(TEST_DIRS) examples
	@echo "$(GREEN)✅ Linting complete!$(RESET)"

type-check:
	@echo "$(BLUE)🏷️  Running type checks...$(RESET)"
	$(PYTHON) -m mypy $(SRC_DIRS) --show-error-codes --pretty
	@echo "$(GREEN)✅ Type checking passed!$(RESET)"

# =====================================================
# Security
# =====================================================

security: security-bandit security-safety security-audit
	@echo "$(GREEN)✅ All security scans complete!$(RESET)"

security-bandit:
	@echo "$(BLUE)🔒 Running Bandit security linter...$(RESET)"
	$(PYTHON) -m bandit $(BANDIT_FLAGS) || true
	$(PYTHON) -m bandit -r $(SRC_DIRS)
	@echo "$(GREEN)✅ Bandit scan complete!$(RESET)"

security-safety:
	@echo "$(BLUE)🔒 Running Safety vulnerability check...$(RESET)"
	$(PYTHON) -m safety scan || true
	@echo "$(GREEN)✅ Safety scan complete!$(RESET)"

security-audit:
	@echo "$(BLUE)🔒 Running pip-audit...$(RESET)"
	$(PYTHON) -m pip_audit --ignore-vuln GHSA-4xh5-x5gv-qwph --ignore-vuln PYSEC-2022-42991 --ignore-vuln GHSA-xqrq-4mgf-ff32 --skip-editable
	@echo "$(GREEN)✅ pip-audit complete!$(RESET)"

# =====================================================
# Testing
# =====================================================

test:
	@echo "$(BLUE)🧪 Running all tests with coverage...$(RESET)"
	$(PYTHON) -m pytest $(TEST_DIRS) -v
	@echo "$(GREEN)✅ All tests passed!$(RESET)"

test-unit:
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	$(PYTHON) -m pytest -m unit -v
	@echo "$(GREEN)✅ Unit tests passed!$(RESET)"

test-cov:
	@echo "$(BLUE)🧪 Running tests with HTML coverage report...$(RESET)"
	$(PYTHON) -m pytest $(TEST_DIRS) --cov=$(PACKAGE) --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated at htmlcov/index.html$(RESET)"

test-quick:
	@echo "$(BLUE)⚡ Running quick tests (no coverage)...$(RESET)"
	$(PYTHON) -m pytest $(TEST_DIRS) -v --tb=short --no-cov
	@echo "$(GREEN)✅ Quick tests passed!$(RESET)"

test-watch:
	@echo "$(BLUE)👀 Running tests in watch mode...$(RESET)"
	$(PYTHON) -m pytest -f $(TEST_DIRS)

# =====================================================
# Documentation
# =====================================================

docs-build:
	@echo "$(BLUE)📚 Building documentation...$(RESET)"
	cd $(DOCS_DIR) && $(PYTHON) -m sphinx -b html . _build/html -W --keep-going
	@echo "$(GREEN)✅ Documentation built at $(DOCS_BUILD)/html/index.html$(RESET)"

docs-serve:
	@echo "$(BLUE)📚 Building and serving documentation...$(RESET)"
	cd $(DOCS_DIR) && $(PYTHON) -m sphinx -b html . _build/html
	@echo "$(GREEN)✅ Opening documentation at http://localhost:8000$(RESET)"
	cd $(DOCS_BUILD)/html && $(PYTHON) -m http.server 8000

docs-clean:
	@echo "$(BLUE)🧹 Cleaning documentation build...$(RESET)"
	rm -rf $(DOCS_BUILD)
	@echo "$(GREEN)✅ Documentation cleaned!$(RESET)"

docs-check:
	@echo "$(BLUE)📚 Verifying documentation build...$(RESET)"
	cd $(DOCS_DIR) && $(PYTHON) -m sphinx -b html . _build/html --keep-going -q
	@echo "$(GREEN)✅ Documentation verified!$(RESET)"

docs-open: docs-build
	@echo "$(BLUE)📚 Opening documentation in browser...$(RESET)"
	@open $(DOCS_BUILD)/html/index.html || xdg-open $(DOCS_BUILD)/html/index.html

# =====================================================
# Build and Release
# =====================================================

build:
	@echo "$(BLUE)📦 Building distributions...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)✅ Build complete! Artifacts in $(DIST_DIR)/$(RESET)"

build-check: clean build
	@echo "$(BLUE)📦 Building and checking package...$(RESET)"
	$(PYTHON) -m twine check $(DIST_DIR)/*
	@echo "$(GREEN)✅ Package verification passed!$(RESET)"

dist-check:
	@echo "$(BLUE)📦 Verifying distributions...$(RESET)"
	$(PYTHON) -m twine check $(DIST_DIR)/*
	@echo "$(GREEN)✅ Distribution check passed!$(RESET)"

publish-test: build-check
	@echo "$(YELLOW)📤 Uploading to Test PyPI...$(RESET)"
	$(PYTHON) -m twine upload --repository testpypi $(DIST_DIR)/*
	@echo "$(GREEN)✅ Upload to Test PyPI complete!$(RESET)"

publish: build-check
	@echo "$(RED)📤 Uploading to production PyPI...$(RESET)"
	@read -p "Are you sure you want to publish to PyPI? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) -m twine upload $(DIST_DIR)/*; \
		echo "$(GREEN)✅ Published to PyPI!$(RESET)"; \
	else \
		echo "$(YELLOW)❌ Publish cancelled$(RESET)"; \
	fi

# =====================================================
# Quality Assurance
# =====================================================

pre-commit:
	@echo "$(BLUE)🪝 Running pre-commit hooks...$(RESET)"
	pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit checks complete!$(RESET)"

check: format-check lint type-check
	@echo "$(GREEN)✅ All code quality checks passed!$(RESET)"

check-ci: check security test
	@echo "$(GREEN)✅ All CI checks passed!$(RESET)"

check-all: check-ci docs-check build-check
	@echo "$(GREEN)✅ All comprehensive checks passed!$(RESET)"

verify-all: clean-all check-all
	@echo "$(BOLD)$(GREEN)✅ Full verification complete! Ready for release.$(RESET)"

# =====================================================
# Utilities
# =====================================================

clean:
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	rm -rf $(BUILD_DIR) $(DIST_DIR) *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleaned!$(RESET)"

clean-all: clean docs-clean
	@echo "$(BLUE)🧹 Deep cleaning...$(RESET)"
	rm -rf htmlcov/ .coverage coverage.xml
	rm -rf bandit-report.json safety-report.json pip-audit-report.json
	@echo "$(GREEN)✅ Deep clean complete!$(RESET)"

deps-update:
	@echo "$(BLUE)🔄 Updating pre-commit hooks...$(RESET)"
	pre-commit autoupdate
	@echo "$(GREEN)✅ Pre-commit hooks updated!$(RESET)"

# =====================================================
# Aliases for convenience
# =====================================================

.PHONY: fmt lint-all qa
fmt: format
lint-all: lint
qa: check
