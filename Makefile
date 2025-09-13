.PHONY: help install install-dev install-ci test test-cov test-unit test-integration test-security test-performance lint lint-fix format format-check clean build upload upload-test verify pre-commit check check-all examples examples-advanced security-scan deps-check type-check docs-build docs-serve docs-clean

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BOLD := \033[1m
RESET := \033[0m

# Python and package info
PYTHON := python
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
	@echo ""
	@echo "$(BOLD)$(GREEN)⚡ Quality Checks:$(RESET)"
	@echo "  pre-commit        Install and run pre-commit hooks on all files"
	@echo "  check             Run fast quality checks (format, lint, unit tests)"
	@echo "  check-all         Run comprehensive quality checks (includes security)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📦 Build & Release:$(RESET)"
	@echo "  clean             Clean all build artifacts, caches, and temporary files"
	@echo "  build             Build wheel and source distribution packages"
	@echo "  verify            Verify built packages for PyPI compliance"
	@echo "  upload-test       Upload to Test PyPI for pre-release testing"
	@echo "  upload            Upload to PyPI (production release)"
	@echo ""
	@echo "$(BOLD)$(GREEN)🎯 Examples & Demos:$(RESET)"
	@echo "  examples          Run basic usage examples"
	@echo "  examples-advanced Run advanced feature demonstrations"
	@echo ""
	@echo "$(BOLD)$(YELLOW)⚡ Quick Workflows:$(RESET)"
	@echo "  dev-check         Quick development cycle (format + lint + test-unit)"
	@echo "  ci-check          CI-style checks (format-check + lint + test-unit + security)"
	@echo "  fix               Auto-fix common issues (format + lint-fix)"

# =====================================================
# Installation and Dependencies
# =====================================================

install:
	@echo "$(BLUE)📦 Installing $(PACKAGE) in development mode...$(RESET)"
	$(PYTHON) -m pip install -e .

install-dev:
	@echo "$(BLUE)🔧 Installing with all development dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[dev,test,security,docs]
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

install-ci:
	@echo "$(BLUE)🤖 Installing for CI environment...$(RESET)"
	$(PYTHON) -m pip install -e .[test,security]

deps-check:
	@echo "$(BLUE)🔍 Checking dependencies for security vulnerabilities...$(RESET)"
	@$(PYTHON) -m pip install --upgrade safety pip-audit 2>/dev/null || true
	@echo "$(YELLOW)Running Safety check...$(RESET)"
	@safety check --short-report || echo "$(YELLOW)⚠️ Safety check completed with warnings$(RESET)"
	@echo "$(YELLOW)Running pip-audit check...$(RESET)"
	@pip-audit --desc --format=text || echo "$(YELLOW)⚠️ Pip-audit completed with warnings$(RESET)"
	@echo "$(GREEN)✅ Dependency security check completed$(RESET)"

# =====================================================
# Code Formatting and Style
# =====================================================

format:
	@echo "$(BLUE)🎨 Formatting code with Ruff...$(RESET)"
	ruff format $(SRC_DIRS)
	@echo "$(GREEN)✅ Code formatted successfully$(RESET)"

format-check:
	@echo "$(BLUE)🔍 Checking code formatting...$(RESET)"
	@if ruff format --check $(SRC_DIRS); then \
		echo "$(GREEN)✅ Code formatting is correct$(RESET)"; \
	else \
		echo "$(RED)❌ Code formatting issues found$(RESET)"; \
		echo "$(YELLOW)💡 Run 'make format' to fix formatting$(RESET)"; \
		exit 1; \
	fi

# =====================================================
# Linting and Type Checking
# =====================================================

lint:
	@echo "$(BLUE)🧹 Running Ruff linting checks...$(RESET)"
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

# =====================================================
# Quality Assurance and Pre-commit
# =====================================================

pre-commit:
	@echo "$(BLUE)🎯 Setting up and running pre-commit hooks...$(RESET)"
	@$(PYTHON) -m pip install pre-commit 2>/dev/null || true
	pre-commit install
	@echo "$(YELLOW)Running pre-commit on all files...$(RESET)"
	pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit hooks installed and executed$(RESET)"

check: format lint type-check test-unit
	@echo "$(GREEN)$(BOLD)✅ Fast quality checks completed successfully!$(RESET)"

check-all: format-check lint type-check security-scan test-unit deps-check
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
	find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

build: clean
	@echo "$(BLUE)📦 Building distribution packages...$(RESET)"
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build --wheel --sdist
	@echo "$(GREEN)✅ Build completed successfully$(RESET)"
	@echo "$(YELLOW)📄 Distribution files:$(RESET)"
	@ls -la dist/

verify: build
	@echo "$(BLUE)🔍 Verifying package integrity and PyPI compliance...$(RESET)"
	@$(PYTHON) -m pip install --upgrade twine
	$(PYTHON) -m twine check dist/*
	@echo "$(YELLOW)Checking package contents...$(RESET)"
	@$(PYTHON) -c "import zipfile; z = zipfile.ZipFile(next(f for f in __import__('glob').glob('dist/*.whl'))); print('Package contents:'); [print(f'  {f}') for f in sorted(z.namelist())[:20]]; print('  ...' if len(z.namelist()) > 20 else '')"
	@echo "$(GREEN)✅ Package verification completed$(RESET)"

upload-test: verify
	@echo "$(BLUE)📤 Uploading to Test PyPI...$(RESET)"
	@echo "$(YELLOW)⚠️ This will upload to https://test.pypi.org$(RESET)"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✅ Package uploaded to Test PyPI$(RESET)"
	@echo "$(YELLOW)🔗 Test installation: pip install --index-url https://test.pypi.org/simple/ nostr-tools$(RESET)"

upload: verify
	@echo "$(BLUE)🚀 Uploading to PyPI (PRODUCTION)...$(RESET)"
	@echo "$(RED)⚠️ WARNING: This will upload to PRODUCTION PyPI!$(RESET)"
	@echo "$(YELLOW)Version: $(VERSION)$(RESET)"
	@read -p "Are you sure you want to release v$(VERSION) to production? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)$(BOLD)🎉 Package successfully released to PyPI!$(RESET)"
	@echo "$(YELLOW)🔗 Installation: pip install nostr-tools$(RESET)"

# =====================================================
# Examples and Demonstrations
# =====================================================

examples:
	@echo "$(BLUE)🎯 Running basic usage examples...$(RESET)"
	@echo "$(YELLOW)ℹ️ Running examples/basic_usage.py$(RESET)"
	@if [ -f "examples/basic_usage.py" ]; then \
		cd examples && $(PYTHON) basic_usage.py; \
	else \
		echo "$(YELLOW)⚠️ examples/basic_usage.py not found$(RESET)"; \
	fi
	@echo "$(GREEN)✅ Basic examples completed successfully$(RESET)"

examples-advanced:
	@echo "$(BLUE)🎯 Running advanced feature demonstrations...$(RESET)"
	@echo "$(YELLOW)ℹ️ Running examples/advanced_features.py$(RESET)"
	@echo "$(YELLOW)⚠️ This may take several minutes and requires network access$(RESET)"
	@if [ -f "examples/advanced_features.py" ]; then \
		cd examples && $(PYTHON) advanced_features.py; \
	else \
		echo "$(YELLOW)⚠️ examples/advanced_features.py not found$(RESET)"; \
	fi
	@echo "$(GREEN)✅ Advanced examples completed successfully$(RESET)"

# =====================================================
# Development Workflow Shortcuts
# =====================================================

dev-check: format lint test-unit
	@echo "$(GREEN)$(BOLD)🔄 Development cycle completed successfully!$(RESET)"
	@echo "$(YELLOW)💡 Ready to commit your changes$(RESET)"

ci-check: format-check lint type-check security-scan test-unit
	@echo "$(GREEN)$(BOLD)🤖 CI-style checks completed successfully!$(RESET)"
	@echo "$(YELLOW)💡 Ready for CI/CD pipeline$(RESET)"

fix: format lint-fix
	@echo "$(GREEN)$(BOLD)🔧 Auto-fixes applied successfully!$(RESET)"
	@echo "$(YELLOW)💡 Review changes and run 'make dev-check' to verify$(RESET)"

# =====================================================
# Project Information
# =====================================================

info:
	@echo "$(BLUE)$(BOLD)ℹ️  nostr-tools v$(VERSION) Project Information$(RESET)"
	@echo ""
	@echo "$(YELLOW)📦 Package Information:$(RESET)"
	@echo "  Name: $(PACKAGE)"
	@echo "  Version: $(VERSION)"
	@echo "  Python: $(shell $(PYTHON) --version 2>&1)"
	@echo ""
	@echo "$(YELLOW)📊 Git Information:$(RESET)"
	@echo "  Branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repository')"
	@echo "  Last commit: $(shell git log -1 --oneline 2>/dev/null || echo 'No commits found')"
	@echo ""
	@echo "$(YELLOW)🔧 Development Tools:$(RESET)"
	@command -v ruff >/dev/null && echo "  Ruff: $(shell ruff --version)" || echo "  Ruff: Not installed"
	@command -v mypy >/dev/null && echo "  MyPy: $(shell mypy --version)" || echo "  MyPy: Not installed"
	@command -v pytest >/dev/null && echo "  Pytest: Available" || echo "  Pytest: Not available"
