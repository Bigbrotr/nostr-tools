# =====================================================
# 🚀 nostr-tools Makefile
# =====================================================
# Development automation and project management commands
# Run 'make help' for available commands
# =====================================================

.PHONY: help install install-dev install-ci test test-cov test-unit test-integration test-performance \
        lint lint-fix format format-check clean build upload upload-test verify pre-commit \
        check check-all examples security-scan deps-check type-check \
        docs-build docs-serve docs-clean docs-watch docs-open docs-links-check docs-coverage-check docs-build-check \
        version

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
DOCS_DIR := docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build
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
	@echo "  test-performance  Run performance benchmarks"
	@echo "  test-cov          Run tests with coverage report"
	@echo ""
	@echo "$(BOLD)$(GREEN)📚 Documentation:$(RESET)"
	@echo "  docs-build        Build documentation"
	@echo "  docs-serve        Serve documentation locally"
	@echo "  docs-watch        Auto-rebuild docs on changes"
	@echo "  docs-open         Build and open docs in browser"
	@echo "  docs-clean        Clean documentation build"
	@echo "  docs-build-check  Build docs with warnings as errors"
	@echo "  docs-links-check  Check documentation links"
	@echo "  docs-coverage-check Check documentation coverage"
	@echo "  docs-check        Run all documentation checks"
	@echo ""
	@echo "$(BOLD)$(GREEN)🔧 Build & Distribution:$(RESET)"
	@echo "  build             Build distribution packages"
	@echo "  clean             Clean build artifacts"
	@echo "  upload            Upload to PyPI"
	@echo "  upload-test       Upload to TestPyPI"
	@echo "  version           Show current version"
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
	@echo "  make docs-open    # Build and view documentation"

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
	$(PYTHON) -m pip install -e ".[test,security,docs]"
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

test-performance:
	@echo "$(BLUE)🧪 Running performance benchmarks...$(RESET)"
	$(PYTHON) -m pytest -m benchmark --benchmark-only

test-cov:
	@echo "$(BLUE)🧪 Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest --cov=src/$(PACKAGE) --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/$(RESET)"

# =====================================================
# Documentation targets
# =====================================================

docs-build:
	@echo "$(BLUE)📚 Building documentation...$(RESET)"
	@if [ ! -d "$(DOCS_DIR)" ]; then \
		echo "$(RED)❌ Documentation directory not found: $(DOCS_DIR)$(RESET)"; \
		exit 1; \
	fi
	cd $(DOCS_DIR) && \
	sphinx-build -b html . _build/html
	@echo "$(GREEN)✅ Documentation built in $(DOCS_BUILD_DIR)/html/$(RESET)"

docs-serve: docs-build
	@echo "$(BLUE)📚 Serving documentation at http://localhost:8000...$(RESET)"
	cd $(DOCS_BUILD_DIR)/html && $(PYTHON) -m http.server 8000

docs-watch:
	@echo "$(BLUE)📚 Auto-rebuilding documentation on changes...$(RESET)"
	@if command -v sphinx-autobuild >/dev/null 2>&1; then \
		cd $(DOCS_DIR) && sphinx-autobuild . _build/html --port 8000 --host 0.0.0.0; \
	else \
		echo "$(YELLOW)sphinx-autobuild not found. Install with: pip install sphinx-autobuild$(RESET)"; \
		echo "$(BLUE)Building once and serving...$(RESET)"; \
		$(MAKE) docs-serve; \
	fi

docs-open: docs-build
	@echo "$(BLUE)📚 Opening documentation in browser...$(RESET)"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$(DOCS_BUILD_DIR)/html/index.html"; \
	elif command -v open >/dev/null 2>&1; then \
		open "$(DOCS_BUILD_DIR)/html/index.html"; \
	else \
		echo "$(YELLOW)Please open $(DOCS_BUILD_DIR)/html/index.html manually$(RESET)"; \
	fi

docs-clean:
	@echo "$(BLUE)🧹 Cleaning documentation build...$(RESET)"
	rm -rf $(DOCS_BUILD_DIR)/*
	rm -rf $(DOCS_DIR)/_autosummary/
	rm -rf $(DOCS_DIR)/_static/
	@echo "$(GREEN)✅ Documentation cleaned!$(RESET)"

docs-build-check:
	@echo "$(BLUE)📚 Building documentation for verification...$(RESET)"
	@if [ ! -d "$(DOCS_DIR)" ]; then \
		echo "$(RED)❌ docs/ directory not found!$(RESET)"; \
		exit 1; \
	fi
	cd $(DOCS_DIR) && \
	sphinx-build -b html . _build/html -W --keep-going -q
	@echo "$(GREEN)✅ Documentation build verification passed$(RESET)"

docs-links-check:
	@echo "$(BLUE)🔗 Checking documentation links...$(RESET)"
	cd $(DOCS_DIR) && \
	sphinx-build -b linkcheck . _build/linkcheck -q
	@if [ -f "$(DOCS_BUILD_DIR)/linkcheck/output.txt" ]; then \
		echo "$(YELLOW)📊 Link check results:$(RESET)"; \
		grep -E "(broken|redirect)" $(DOCS_BUILD_DIR)/linkcheck/output.txt | head -10 || echo "$(GREEN)✅ No broken links found$(RESET)"; \
	fi

docs-coverage-check:
	@echo "$(BLUE)📊 Checking documentation coverage...$(RESET)"
	cd $(DOCS_DIR) && \
	sphinx-build -b coverage . _build/coverage -q
	@if [ -f "$(DOCS_BUILD_DIR)/coverage/python.txt" ]; then \
		echo "$(YELLOW)📈 Documentation coverage report:$(RESET)"; \
		head -20 $(DOCS_BUILD_DIR)/coverage/python.txt; \
		echo ""; \
		echo "$(BLUE)💡 Full report available at: $(DOCS_BUILD_DIR)/coverage/python.txt$(RESET)"; \
	else \
		echo "$(RED)❌ Coverage report not generated$(RESET)"; \
		exit 1; \
	fi

docs-check:
	@echo "$(BLUE)🔍 Running all documentation checks...$(RESET)"
	@$(MAKE) docs-build-check
	@$(MAKE) docs-links-check
	@$(MAKE) docs-coverage-check
	@echo "$(GREEN)✅ All documentation checks passed!$(RESET)"

# =====================================================
# Build and distribution targets
# =====================================================

clean:
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	rm -rf build/ dist/ *.egg-info
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf .mypy_cache/ .ruff_cache/
	rm -rf bandit-report.json
	rm -rf .benchmarks/
	rm -rf $(DOCS_BUILD_DIR)/*
	rm -rf $(DOCS_DIR)/_autosummary/
	rm -rf $(DOCS_DIR)/_static/
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
# Quality assurance targets
# =====================================================

check:
	@echo "$(BOLD)$(BLUE)🔍 Running quality checks...$(RESET)"
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) test
	@$(MAKE) docs-check
	@echo "$(GREEN)✅ All quality checks passed!$(RESET)"

check-all:
	@echo "$(BOLD)$(BLUE)🔍 Running comprehensive quality checks...$(RESET)"
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) security-scan
	@$(MAKE) test-cov
	@$(MAKE) docs-check
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

examples:
	@echo "$(BLUE)🚀 Running example scripts...$(RESET)"
	@if [ -d "examples" ]; then \
		for script in examples/*.py; do \
			if [ -f "$$script" ]; then \
				echo "$(YELLOW)Running $$script...$(RESET)"; \
				$(PYTHON) "$$script" || echo "$(RED)❌ $$script failed$(RESET)"; \
			fi; \
		done; \
	else \
		echo "$(YELLOW)⚠️ No examples directory found$(RESET)"; \
	fi

verify:
	@echo "$(BLUE)🔍 Verifying installation...$(RESET)"
	$(PYTHON) -c "import $(PACKAGE); print(f'✅ $(PACKAGE) v{$(PACKAGE).__version__} imported successfully')"
	@echo "$(GREEN)✅ Installation verified!$(RESET)"

version:
	@echo "$(BOLD)nostr-tools version: $(GREEN)$(VERSION)$(RESET)"
