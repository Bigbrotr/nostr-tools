.PHONY: help install install-dev install-ci test test-cov test-unit test-integration test-security test-performance lint lint-fix format format-check format-all clean build upload upload-test verify pre-commit check check-all examples examples-advanced security-scan deps-check

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Python and package info
PYTHON := python
PACKAGE := nostr_tools
SRC_DIRS := $(PACKAGE) tests examples

# Default target
help:
	@echo "$(BLUE)🚀 nostr-tools Development Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Setup:$(RESET)"
	@echo "  install           Install package in development mode"
	@echo "  install-dev       Install with all development dependencies"
	@echo "  install-ci        Install for CI environment"
	@echo "  deps-check        Check for dependency vulnerabilities"
	@echo ""
	@echo "$(GREEN)Code Quality:$(RESET)"
	@echo "  format            Format all code with Ruff"
	@echo "  format-check      Check code formatting without changes"
	@echo "  format-all        Format all files including notebooks"
	@echo "  lint              Run all linting (Ruff + MyPy)"
	@echo "  lint-fix          Run linting with auto-fix"
	@echo "  security-scan     Run security checks"
	@echo ""
	@echo "$(GREEN)Testing:$(RESET)"
	@echo "  test              Run all tests"
	@echo "  test-unit         Run only unit tests (fast)"
	@echo "  test-integration  Run integration tests"
	@echo "  test-security     Run security-focused tests"
	@echo "  test-performance  Run performance tests"
	@echo "  test-cov          Run tests with coverage report"
	@echo ""
	@echo "$(GREEN)Pre-commit & Quality:$(RESET)"
	@echo "  pre-commit        Install and run pre-commit hooks"
	@echo "  check             Run all quality checks (fast)"
	@echo "  check-all         Run comprehensive quality checks"
	@echo ""
	@echo "$(GREEN)Build & Release:$(RESET)"
	@echo "  clean             Clean build artifacts and caches"
	@echo "  build             Build package for distribution"
	@echo "  verify            Verify package before release"
	@echo "  upload-test       Upload to Test PyPI"
	@echo "  upload            Upload to PyPI"
	@echo ""
	@echo "$(GREEN)Examples & Docs:$(RESET)"
	@echo "  examples          Run basic examples"
	@echo "  examples-advanced Run advanced examples"
	@echo ""
	@echo "$(YELLOW)Quick Commands:$(RESET)"
	@echo "  make dev-check    # Quick development check"
	@echo "  make ci-check     # Full CI-style check"
	@echo "  make fix          # Auto-fix common issues"

# Installation targets
install:
	@echo "$(BLUE)📦 Installing $(PACKAGE) in development mode...$(RESET)"
	$(PYTHON) -m pip install -e .

install-dev:
	@echo "$(BLUE)🔧 Installing with all development dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[dev,test,security,docs]

install-ci:
	@echo "$(BLUE)🤖 Installing for CI environment...$(RESET)"
	$(PYTHON) -m pip install -e .[test,security]

deps-check:
	@echo "$(BLUE)🔍 Checking dependencies for vulnerabilities...$(RESET)"
	$(PYTHON) -m pip install safety pip-audit
	safety check --short-report
	pip-audit --desc --format=text

# Code formatting
format:
	@echo "$(BLUE)🎨 Formatting code with Ruff...$(RESET)"
	ruff format $(SRC_DIRS)
	@echo "$(GREEN)✅ Code formatted successfully$(RESET)"

format-check:
	@echo "$(BLUE)🔍 Checking code formatting...$(RESET)"
	ruff format --check $(SRC_DIRS)
	@echo "$(GREEN)✅ Code formatting is correct$(RESET)"

format-all: format
	@echo "$(BLUE)🎨 Formatting all files including notebooks...$(RESET)"
	@command -v jupyter >/dev/null 2>&1 && find . -name "*.ipynb" -exec jupyter nbconvert --clear-output --inplace {} \; || echo "Jupyter not available, skipping notebooks"

# Linting
lint:
	@echo "$(BLUE)🧹 Running linters...$(RESET)"
	ruff check $(SRC_DIRS)
	mypy $(PACKAGE) --ignore-missing-imports --show-error-codes
	@echo "$(GREEN)✅ All linting checks passed$(RESET)"

lint-fix:
	@echo "$(BLUE)🔧 Running linters with auto-fix...$(RESET)"
	ruff check --fix $(SRC_DIRS)
	mypy $(PACKAGE) --ignore-missing-imports --show-error-codes
	@echo "$(GREEN)✅ Linting completed with fixes$(RESET)"

# Security scanning
security-scan:
	@echo "$(BLUE)🔒 Running security scans...$(RESET)"
	bandit -r $(PACKAGE) -f text --severity-level medium
	@echo "$(GREEN)✅ Security scan completed$(RESET)"

# Testing
test:
	@echo "$(BLUE)🧪 Running all tests...$(RESET)"
	$(PYTHON) -m pytest -v
	@echo "$(GREEN)✅ All tests completed$(RESET)"

test-unit:
	@echo "$(BLUE)⚡ Running unit tests...$(RESET)"
	$(PYTHON) -m pytest -m "not integration and not slow" -v
	@echo "$(GREEN)✅ Unit tests completed$(RESET)"

test-integration:
	@echo "$(BLUE)🌐 Running integration tests...$(RESET)"
	$(PYTHON) -m pytest -m integration -v -s
	@echo "$(GREEN)✅ Integration tests completed$(RESET)"

test-security:
	@echo "$(BLUE)🔐 Running security tests...$(RESET)"
	$(PYTHON) -m pytest -m security -v
	@echo "$(GREEN)✅ Security tests completed$(RESET)"

test-performance:
	@echo "$(BLUE)🏃 Running performance tests...$(RESET)"
	$(PYTHON) -m pytest -m slow -v --tb=short
	@echo "$(GREEN)✅ Performance tests completed$(RESET)"

test-cov:
	@echo "$(BLUE)📊 Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "$(GREEN)📄 Coverage report generated in htmlcov/$(RESET)"

# Pre-commit and quality checks
pre-commit:
	@echo "$(BLUE)🎯 Setting up and running pre-commit hooks...$(RESET)"
	$(PYTHON) -m pip install pre-commit
	pre-commit install
	pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit hooks installed and executed$(RESET)"

check: format-check lint test-unit
	@echo "$(GREEN)✅ Fast quality checks completed successfully!$(RESET)"

check-all: format-check lint security-scan test-unit deps-check
	@echo "$(GREEN)✅ All quality checks completed successfully!$(RESET)"

# Build and release
clean:
	@echo "$(BLUE)🧹 Cleaning build artifacts and caches...$(RESET)"
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf .coverage htmlcov/ coverage.xml
	rm -rf .tox/ .nox/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

build: clean
	@echo "$(BLUE)📦 Building package...$(RESET)"
	$(PYTHON) -m build --wheel --sdist
	@echo "$(GREEN)✅ Package built successfully$(RESET)"
	@ls -la dist/

verify: build
	@echo "$(BLUE)🔍 Verifying package...$(RESET)"
	$(PYTHON) -m twine check dist/*
	@echo "$(GREEN)✅ Package verification completed$(RESET)"

upload-test: verify
	@echo "$(BLUE)📤 Uploading to Test PyPI...$(RESET)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✅ Package uploaded to Test PyPI$(RESET)"

upload: verify
	@echo "$(BLUE)🚀 Uploading to PyPI...$(RESET)"
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✅ Package uploaded to PyPI$(RESET)"

# Examples
examples:
	@echo "$(BLUE)🎯 Running basic examples...$(RESET)"
	cd examples && $(PYTHON) basic_usage.py
	@echo "$(GREEN)✅ Basic examples completed$(RESET)"

examples-advanced:
	@echo "$(BLUE)🎯 Running advanced examples...$(RESET)"
	cd examples && $(PYTHON) advanced_features.py
	@echo "$(GREEN)✅ Advanced examples completed$(RESET)"

# Development workflow shortcuts
dev-check: format lint test-unit
	@echo "$(GREEN)🔄 Development cycle completed successfully!$(RESET)"

ci-check: format-check lint security-scan test-unit
	@echo "$(GREEN)🤖 CI-style checks completed successfully!$(RESET)"

fix: format lint-fix
	@echo "$(GREEN)🔧 Auto-fixes applied successfully!$(RESET)"

# Release workflow
release-check: clean check-all verify
	@echo "$(GREEN)🚀 Ready for release!$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Release checklist:$(RESET)"
	@echo "  ✅ Code formatted and linted"
	@echo "  ✅ All tests passing"
	@echo "  ✅ Security checks passed"
	@echo "  ✅ Package verified"
	@echo ""
	@echo "$(BLUE)💡 Next steps:$(RESET)"
	@echo "  1. Update version in pyproject.toml"
	@echo "  2. Update CHANGELOG.md"
	@echo "  3. Create release PR"
	@echo "  4. Tag release after merge"
	@echo "  5. Run 'make upload' to publish"

# Debugging and info
info:
	@echo "$(BLUE)ℹ️  Project Information:$(RESET)"
	@echo "  Python: $$($(PYTHON) --version)"
	@echo "  Pip: $$($(PYTHON) -m pip --version)"
	@echo "  Package: $(PACKAGE)"
	@echo "  Location: $$(pwd)"
	@echo "  Git branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repository')"
	@echo "  Git status: $$(git status --porcelain 2>/dev/null | wc -l || echo 'N/A') files changed"

validate-env:
	@echo "$(BLUE)🔍 Validating environment...$(RESET)"
	@$(PYTHON) -c "import sys; print(f'Python: {sys.version}')"
	@$(PYTHON) -c "import $(PACKAGE); print(f'$(PACKAGE): {$(PACKAGE).__version__}')" 2>/dev/null || echo "$(PACKAGE) not installed"
	@command -v ruff >/dev/null && ruff --version || echo "Ruff not available"
	@command -v mypy >/dev/null && mypy --version || echo "MyPy not available"
	@echo "$(GREEN)✅ Environment validated$(RESET)"

# Watch mode for development (requires entr)
watch-test:
	@echo "$(BLUE)👀 Watching for changes to run tests...$(RESET)"
	@command -v entr >/dev/null 2>&1 || (echo "$(RED)entr not found. Install with: brew install entr$(RESET)" && exit 1)
	find $(SRC_DIRS) -name "*.py" | entr -c make test-unit

watch-lint:
	@echo "$(BLUE)👀 Watching for changes to run linting...$(RESET)"
	@command -v entr >/dev/null 2>&1 || (echo "$(RED)entr not found. Install with: brew install entr$(RESET)" && exit 1)
	find $(SRC_DIRS) -name "*.py" | entr -c make lint
