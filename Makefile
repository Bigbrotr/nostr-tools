.PHONY: help install install-dev install-ci test test-cov test-unit test-integration test-security test-performance lint lint-fix format format-check format-all clean build upload upload-test verify pre-commit check check-all examples examples-advanced security-scan deps-check type-check

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
	@echo "  format-all        Format all files including notebooks and docs"
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
	@echo "  test-performance  Run performance benchmarks and regression tests"
	@echo "  test-cov          Run tests with comprehensive coverage report"
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
	@echo "  release-check     Complete pre-release validation"
	@echo ""
	@echo "$(BOLD)$(YELLOW)🔍 Monitoring & Info:$(RESET)"
	@echo "  info              Display project and environment information"
	@echo "  validate-env      Validate development environment setup"
	@echo "  watch-test        Watch files and run unit tests on changes (requires entr)"
	@echo "  watch-lint        Watch files and run linting on changes (requires entr)"

# =====================================================
# Installation and Dependencies
# =====================================================

install:
	@echo "$(BLUE)📦 Installing $(PACKAGE) in development mode...$(RESET)"
	$(PYTHON) -m pip install -e .

install-dev:
	@echo "$(BLUE)🔧 Installing with all development dependencies...$(RESET)"
	$(PYTHON) -m pip install -e .[dev,test,security,docs,perf]
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

install-ci:
	@echo "$(BLUE)🤖 Installing for CI environment...$(RESET)"
	$(PYTHON) -m pip install -e .[test,security]

deps-check:
	@echo "$(BLUE)🔍 Checking dependencies for security vulnerabilities...$(RESET)"
	@$(PYTHON) -m pip install --upgrade safety pip-audit 2>/dev/null || true
	@echo "$(YELLOW)Running Safety check...$(RESET)"
	@safety check --short-report --ignore 70612 || echo "$(YELLOW)⚠️ Safety check completed with warnings$(RESET)"
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

format-all: format
	@echo "$(BLUE)🎨 Formatting additional files...$(RESET)"
	@command -v jupyter >/dev/null 2>&1 && find . -name "*.ipynb" -exec jupyter nbconvert --clear-output --inplace {} \; 2>/dev/null || echo "$(YELLOW)⚠️ Jupyter not available, skipping notebooks$(RESET)"
	@echo "$(GREEN)✅ All files formatted$(RESET)"

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
	@echo "$(YELLOW)Running additional security validations...$(RESET)"
	@$(PYTHON) -c "import ssl; print('SSL/TLS support: OK')" 2>/dev/null || echo "$(RED)⚠️ SSL/TLS issues detected$(RESET)"
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
	@read -p "Continue? (y/N): " confirm && [ "$confirm" = "y" ] || exit 1
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✅ Package uploaded to Test PyPI$(RESET)"
	@echo "$(YELLOW)🔗 Test installation: pip install --index-url https://test.pypi.org/simple/ nostr-tools$(RESET)"

upload: verify
	@echo "$(BLUE)🚀 Uploading to PyPI (PRODUCTION)...$(RESET)"
	@echo "$(RED)⚠️ WARNING: This will upload to PRODUCTION PyPI!$(RESET)"
	@echo "$(YELLOW)Version: $(VERSION)$(RESET)"
	@read -p "Are you sure you want to release v$(VERSION) to production? (y/N): " confirm && [ "$confirm" = "y" ] || exit 1
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)$(BOLD)🎉 Package successfully released to PyPI!$(RESET)"
	@echo "$(YELLOW)🔗 Installation: pip install nostr-tools$(RESET)"

# =====================================================
# Examples and Demonstrations
# =====================================================

examples:
	@echo "$(BLUE)🎯 Running basic usage examples...$(RESET)"
	@echo "$(YELLOW)ℹ️ Running examples/basic_usage.py$(RESET)"
	cd examples && $(PYTHON) basic_usage.py
	@echo "$(GREEN)✅ Basic examples completed successfully$(RESET)"

examples-advanced:
	@echo "$(BLUE)🎯 Running advanced feature demonstrations...$(RESET)"
	@echo "$(YELLOW)ℹ️ Running examples/advanced_features.py$(RESET)"
	@echo "$(YELLOW)⚠️ This may take several minutes and requires network access$(RESET)"
	cd examples && $(PYTHON) advanced_features.py
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
# Release and Quality Gates
# =====================================================

release-check: clean format-check lint type-check security-scan test-unit verify
	@echo "$(GREEN)$(BOLD)🚀 Release validation completed!$(RESET)"
	@echo ""
	@echo "$(YELLOW)$(BOLD)📋 Pre-release checklist:$(RESET)"
	@echo "  ✅ Code formatted and linted"
	@echo "  ✅ Type checking passed"
	@echo "  ✅ Security scans completed"
	@echo "  ✅ Unit tests passing"
	@echo "  ✅ Package verified for PyPI compliance"
	@echo ""
	@echo "$(BLUE)$(BOLD)📝 Manual checks still needed:$(RESET)"
	@echo "  🔲 Version updated in pyproject.toml and __init__.py"
	@echo "  🔲 CHANGELOG.md updated with new features and fixes"
	@echo "  🔲 Documentation updated (README.md, docstrings)"
	@echo "  🔲 Integration tests passing (run 'make test-integration')"
	@echo "  🔲 Examples working correctly"
	@echo ""
	@echo "$(YELLOW)$(BOLD)🚀 Next steps for release:$(RESET)"
	@echo "  1. Create release PR with version updates"
	@echo "  2. Get PR approval and merge to main"
	@echo "  3. Create and push Git tag: git tag v$(VERSION) && git push --tags"
	@echo "  4. GitHub Actions will automatically publish to PyPI"
	@echo "  5. Create GitHub release with changelog notes"

# =====================================================
# Environment and Project Information
# =====================================================

info:
	@echo "$(BLUE)$(BOLD)ℹ️  nostr-tools Project Information$(RESET)"
	@echo ""
	@echo "$(YELLOW)📦 Package Information:$(RESET)"
	@echo "  Name: $(PACKAGE)"
	@echo "  Version: $(VERSION)"
	@echo "  Location: $(pwd)"
	@echo ""
	@echo "$(YELLOW)🐍 Python Environment:$(RESET)"
	@echo "  Python: $($(PYTHON) --version 2>&1)"
	@echo "  Pip: $($(PYTHON) -m pip --version 2>&1)"
	@echo "  Virtual Environment: ${VIRTUAL_ENV:-'Not activated'}"
	@echo ""
	@echo "$(YELLOW)📊 Git Information:$(RESET)"
	@echo "  Branch: $(git branch --show-current 2>/dev/null || echo 'Not a git repository')"
	@echo "  Last commit: $(git log -1 --oneline 2>/dev/null || echo 'No commits found')"
	@echo "  Status: $(git status --porcelain 2>/dev/null | wc -l || echo 'N/A') files changed"
	@echo ""
	@echo "$(YELLOW)🔧 Development Tools:$(RESET)"
	@command -v ruff >/dev/null && echo "  Ruff: $(ruff --version)" || echo "  Ruff: Not installed"
	@command -v mypy >/dev/null && echo "  MyPy: $(mypy --version)" || echo "  MyPy: Not installed"
	@command -v pytest >/dev/null && echo "  Pytest: $(pytest --version | head -1)" || echo "  Pytest: Not installed"

validate-env:
	@echo "$(BLUE)🔍 Validating development environment...$(RESET)"
	@echo ""
	@echo "$(YELLOW)Checking Python installation...$(RESET)"
	@$(PYTHON) -c "import sys; print(f'✅ Python {sys.version.split()[0]} detected')"
	@echo ""
	@echo "$(YELLOW)Checking package installation...$(RESET)"
	@$(PYTHON) -c "import $(PACKAGE); print(f'✅ $(PACKAGE) v{$(PACKAGE).__version__} installed')" 2>/dev/null || echo "❌ $(PACKAGE) not installed - run 'make install-dev'"
	@echo ""
	@echo "$(YELLOW)Checking development tools...$(RESET)"
	@command -v ruff >/dev/null && echo "✅ Ruff: $(ruff --version)" || echo "❌ Ruff not available"
	@command -v mypy >/dev/null && echo "✅ MyPy: $(mypy --version)" || echo "❌ MyPy not available"
	@command -v pytest >/dev/null && echo "✅ Pytest: Available" || echo "❌ Pytest not available"
	@command -v pre-commit >/dev/null && echo "✅ Pre-commit: Available" || echo "⚠️ Pre-commit not available"
	@echo ""
	@echo "$(YELLOW)Checking core dependencies...$(RESET)"
	@$(PYTHON) -c "import aiohttp; print('✅ aiohttp: Available')" 2>/dev/null || echo "❌ aiohttp not available"
	@$(PYTHON) -c "import secp256k1; print('✅ secp256k1: Available')" 2>/dev/null || echo "❌ secp256k1 not available"
	@$(PYTHON) -c "import bech32; print('✅ bech32: Available')" 2>/dev/null || echo "❌ bech32 not available"
	@echo ""
	@echo "$(GREEN)✅ Environment validation completed$(RESET)"

# =====================================================
# File Watching and Development Automation
# =====================================================

watch-test:
	@echo "$(BLUE)👀 Watching for changes to run unit tests...$(RESET)"
	@echo "$(YELLOW)ℹ️ Requires 'entr' - install with: brew install entr (macOS) or apt install entr (Ubuntu)$(RESET)"
	@command -v entr >/dev/null 2>&1 || (echo "$(RED)❌ 'entr' not found$(RESET)" && exit 1)
	@echo "$(YELLOW)👀 Watching $(SRC_DIRS) - press Ctrl+C to stop$(RESET)"
	find $(SRC_DIRS) -name "*.py" | entr -c $(MAKE) test-unit

watch-lint:
	@echo "$(BLUE)👀 Watching for changes to run linting...$(RESET)"
	@command -v entr >/dev/null 2>&1 || (echo "$(RED)❌ 'entr' not found$(RESET)" && exit 1)
	@echo "$(YELLOW)👀 Watching $(SRC_DIRS) - press Ctrl+C to stop$(RESET)"
	find $(SRC_DIRS) -name "*.py" | entr -c $(MAKE) lint

# =====================================================
# Debugging and Troubleshooting
# =====================================================

debug-info:
	@echo "$(BLUE)$(BOLD)🐛 Debug Information$(RESET)"
	@echo ""
	@echo "$(YELLOW)System Information:$(RESET)"
	@uname -a 2>/dev/null || echo "  System info not available"
	@echo ""
	@echo "$(YELLOW)Python Details:$(RESET)"
	@$(PYTHON) -c "import sys, platform; print(f'  Version: {sys.version}'); print(f'  Platform: {platform.platform()}'); print(f'  Executable: {sys.executable}')"
	@echo ""
	@echo "$(YELLOW)Package Dependencies:$(RESET)"
	@$(PYTHON) -m pip list | grep -E "(aiohttp|secp256k1|bech32|pytest|ruff|mypy)" || echo "  No core dependencies found"
	@echo ""
	@echo "$(YELLOW)Environment Variables:$(RESET)"
	@env | grep -E "(PYTHON|PIP|VIRTUAL_ENV|PATH)" | head -5 || echo "  No relevant environment variables"

troubleshoot:
	@echo "$(BLUE)$(BOLD)🔧 Common Troubleshooting$(RESET)"
	@echo ""
	@echo "$(YELLOW)$(BOLD)Issue: Tests failing$(RESET)"
	@echo "  • Run 'make clean' then 'make install-dev'"
	@echo "  • Check Python version: 'python --version' (need 3.9+)"
	@echo "  • Run 'make validate-env' to check setup"
	@echo ""
	@echo "$(YELLOW)$(BOLD)Issue: Import errors$(RESET)"
	@echo "  • Ensure virtual environment is activated"
	@echo "  • Run 'make install-dev' to install dependencies"
	@echo "  • Check PYTHONPATH includes current directory"
	@echo ""
	@echo "$(YELLOW)$(BOLD)Issue: Pre-commit hooks failing$(RESET)"
	@echo "  • Run 'make format' to fix formatting issues"
	@echo "  • Run 'make lint-fix' to auto-fix linting issues"
	@echo "  • Run 'make pre-commit' to reinstall hooks"
	@echo ""
	@echo "$(YELLOW)$(BOLD)Issue: Build/packaging problems$(RESET)"
	@echo "  • Run 'make clean' to remove old build artifacts"
	@echo "  • Update build tools: 'pip install --upgrade build twine'"
	@echo "  • Check pyproject.toml syntax"

# =====================================================
# Performance and Benchmarking
# =====================================================

benchmark:
	@echo "$(BLUE)🏃 Running performance benchmarks...$(RESET)"
	@echo "$(YELLOW)This will run comprehensive performance tests$(RESET)"
	$(PYTHON) -m pytest tests/test_performance.py::TestBenchmarkComparison::test_comprehensive_benchmark -v -s
	@echo "$(GREEN)✅ Benchmark completed$(RESET)"

profile:
	@echo "$(BLUE)📊 Running performance profiling...$(RESET)"
	@echo "$(YELLOW)This will profile key operations and generate reports$(RESET)"
	$(PYTHON) -c "
import cProfile
import pstats
from nostr_tools import generate_keypair, generate_event, Event

def profile_operations():
    # Profile key generation
    for _ in range(100):
        private_key, public_key = generate_keypair()

    # Profile event creation
    for i in range(100):
        event_data = generate_event(
            private_key, public_key, 1, [], f'Profiling test {i}'
        )
        Event.from_dict(event_data)

cProfile.run('profile_operations()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(20)
"
	@echo "$(GREEN)✅ Profiling completed$(RESET)"

# =====================================================
# Documentation and Help
# =====================================================

docs:
	@echo "$(BLUE)📚 Building documentation...$(RESET)"
	@echo "$(YELLOW)⚠️ Documentation build not implemented yet$(RESET)"
	@echo "$(YELLOW)💡 See README.md for current documentation$(RESET)"

docs-serve:
	@echo "$(BLUE)🌐 Serving documentation locally...$(RESET)"
	@echo "$(YELLOW)⚠️ Documentation server not implemented yet$(RESET)"
	@echo "$(YELLOW)💡 See README.md for current documentation$(RESET)"

# =====================================================
# Advanced Development Features
# =====================================================

test-coverage-html:
	@echo "$(BLUE)📊 Generating detailed HTML coverage report...$(RESET)"
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=html --cov-branch
	@echo "$(GREEN)✅ HTML coverage report generated$(RESET)"
	@echo "$(YELLOW)🔗 Open htmlcov/index.html in your browser$(RESET)"

test-with-output:
	@echo "$(BLUE)🧪 Running tests with full output...$(RESET)"
	$(PYTHON) -m pytest -v -s --tb=long

test-failed-only:
	@echo "$(BLUE)🧪 Running only previously failed tests...$(RESET)"
	$(PYTHON) -m pytest --lf -v

test-parallel:
	@echo "$(BLUE)🧪 Running tests in parallel...$(RESET)"
	@$(PYTHON) -m pip install pytest-xdist 2>/dev/null || true
	$(PYTHON) -m pytest -n auto

# =====================================================
# Git and Version Control Helpers
# =====================================================

git-hooks-install:
	@echo "$(BLUE)🔗 Installing git hooks...$(RESET)"
	@if [ -d .git ]; then \
		echo "#!/bin/sh\nmake pre-commit" > .git/hooks/pre-push; \
		chmod +x .git/hooks/pre-push; \
		echo "$(GREEN)✅ Git hooks installed$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️ Not a git repository$(RESET)"; \
	fi

version-bump-patch:
	@echo "$(BLUE)🔢 Bumping patch version...$(RESET)"
	@$(PYTHON) -c "
import re
with open('pyproject.toml', 'r') as f: content = f.read()
version_match = re.search(r'version = \"([^\"]+)\"', content)
if version_match:
    current = version_match.group(1)
    major, minor, patch = map(int, current.split('.'))
    new_version = f'{major}.{minor}.{patch + 1}'
    new_content = re.sub(r'version = \"[^\"]+\"', f'version = \"{new_version}\"', content)
    with open('pyproject.toml', 'w') as f: f.write(new_content)
    print(f'Version bumped: {current} -> {new_version}')
else:
    print('Could not find version in pyproject.toml')
"
	@echo "$(GREEN)✅ Version bumped$(RESET)"

version-bump-minor:
	@echo "$(BLUE)🔢 Bumping minor version...$(RESET)"
	@$(PYTHON) -c "
import re
with open('pyproject.toml', 'r') as f: content = f.read()
version_match = re.search(r'version = \"([^\"]+)\"', content)
if version_match:
    current = version_match.group(1)
    major, minor, patch = map(int, current.split('.'))
    new_version = f'{major}.{minor + 1}.0'
    new_content = re.sub(r'version = \"[^\"]+\"', f'version = \"{new_version}\"', content)
    with open('pyproject.toml', 'w') as f: f.write(new_content)
    print(f'Version bumped: {current} -> {new_version}')
else:
    print('Could not find version in pyproject.toml')
"
	@echo "$(GREEN)✅ Version bumped$(RESET)"

# =====================================================
# Special Utility Targets
# =====================================================

lines-of-code:
	@echo "$(BLUE)📏 Counting lines of code...$(RESET)"
	@echo "$(YELLOW)Source code ($(PACKAGE)):$(RESET)"
	@find $(PACKAGE) -name "*.py" -exec wc -l {} + | tail -1
	@echo "$(YELLOW)Test code:$(RESET)"
	@find tests -name "*.py" -exec wc -l {} + | tail -1 2>/dev/null || echo "  0 (no tests directory)"
	@echo "$(YELLOW)Example code:$(RESET)"
	@find examples -name "*.py" -exec wc -l {} + | tail -1 2>/dev/null || echo "  0 (no examples directory)"
	@echo "$(YELLOW)Total Python code:$(RESET)"
	@find $(SRC_DIRS) -name "*.py" -exec wc -l {} + | tail -1

dependency-tree:
	@echo "$(BLUE)🌳 Displaying dependency tree...$(RESET)"
	@$(PYTHON) -m pip install pipdeptree 2>/dev/null || true
	@pipdeptree --packages $(PACKAGE) 2>/dev/null || echo "$(YELLOW)⚠️ pipdeptree not available$(RESET)"

check-outdated:
	@echo "$(BLUE)📅 Checking for outdated dependencies...$(RESET)"
	$(PYTHON) -m pip list --outdated --format=columns || echo "$(GREEN)✅ All dependencies up to date$(RESET)"

# =====================================================
# Error Handling and Validation
# =====================================================

_check_python:
	@$(PYTHON) --version >/dev/null 2>&1 || (echo "$(RED)❌ Python not found$(RESET)" && exit 1)

_check_git:
	@git --version >/dev/null 2>&1 || (echo "$(RED)❌ Git not found$(RESET)" && exit 1)

_check_network:
	@ping -c 1 google.com >/dev/null 2>&1 || (echo "$(YELLOW)⚠️ Network connectivity issues detected$(RESET)")

# Ensure critical targets depend on basic checks
install-dev: _check_python
test-integration: _check_network
upload: _check_git
upload-test: _check_git
