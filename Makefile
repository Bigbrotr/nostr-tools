.PHONY: help install install-dev test test-cov lint format clean build upload upload-test check

# Default target
help:
	@echo "🚀 nostr-tools Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install the package"
	@echo "  install-dev   Install with development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  format        Format code with Ruff"
	@echo "  format-check  Check code formatting"
	@echo "  lint          Run linting (Ruff + MyPy)"
	@echo "  lint-fix      Run linting and fix issues"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  test-unit     Run only unit tests"
	@echo "  test-fast     Run fast tests only"
	@echo ""
	@echo "Build & Release:"
	@echo "  build         Build package"
	@echo "  upload-test   Upload to Test PyPI"
	@echo "  upload        Upload to PyPI"
	@echo "  verify        Verify package before release"
	@echo ""
	@echo "Utilities:"
	@echo "  clean         Clean build artifacts"
	@echo "  check         Run all quality checks"
	@echo "  examples      Run example scripts"

# Installation
install:
	@echo "📦 Installing nostr-tools..."
	pip install -e .

install-dev:
	@echo "🔧 Installing development dependencies..."
	pip install -e .[dev,test]

# Code formatting
format:
	@echo "🎨 Formatting code with Ruff..."
	ruff format nostr_tools tests examples
	ruff check --fix nostr_tools tests examples

format-check:
	@echo "🔍 Checking code formatting..."
	ruff format --check nostr_tools tests examples
	ruff check nostr_tools tests examples

# Linting
lint:
	@echo "🧹 Running linters..."
	ruff check nostr_tools tests examples
	mypy nostr_tools --ignore-missing-imports

lint-fix:
	@echo "🔧 Running linters with auto-fix..."
	ruff check --fix nostr_tools tests examples
	mypy nostr_tools --ignore-missing-imports

# Testing
test:
	@echo "🧪 Running all tests..."
	python -m pytest

test-cov:
	@echo "📊 Running tests with coverage..."
	python -m pytest --cov=nostr_tools --cov-report=html --cov-report=term-missing
	@echo "📄 Coverage report generated in htmlcov/"

test-unit:
	@echo "⚡ Running unit tests..."
	python -m pytest -m "unit" -v

test-fast:
	@echo "🏃 Running fast tests only..."
	python -m pytest -m "not slow and not integration" -v

# Build and release
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

build: clean
	@echo "📦 Building package..."
	python -m build
	@echo "✅ Package built successfully"

verify: build
	@echo "🔍 Verifying package..."
	python -m twine check dist/*
	@echo "✅ Package verification complete"

upload-test: verify
	@echo "📤 Uploading to Test PyPI..."
	python -m twine upload --repository testpypi dist/*

upload: verify
	@echo "🚀 Uploading to PyPI..."
	python -m twine upload dist/*

# Examples
examples:
	@echo "🎯 Running basic examples..."
	python examples/basic_usage.py

examples-advanced:
	@echo "🎯 Running advanced examples..."
	python examples/advanced_features.py

# Quality checks
check: format-check lint test-unit
	@echo "✅ All quality checks passed!"

check-fast: format-check lint test-fast
	@echo "⚡ Fast quality checks passed!"

# Release preparation
pre-release: clean check verify
	@echo "🚀 Ready for release!"
	@echo ""
	@echo "📋 Release checklist:"
	@echo "  ✅ Code formatted and linted"
	@echo "  ✅ All tests passing"
	@echo "  ✅ Package verified"
	@echo ""
	@echo "💡 Next steps:"
	@echo "  1. Update version in pyproject.toml"
	@echo "  2. Update CHANGELOG.md"
	@echo "  3. Create release PR"
	@echo "  4. Tag release after merge"
	@echo "  5. Run 'make upload' to publish"

# Development workflow
dev-test: format lint test-unit
	@echo "🔄 Development cycle complete"

# Debugging
info:
	@echo "ℹ️  Project info:"
	@echo "  Python: $(shell python --version)"
	@echo "  Pip: $(shell pip --version)"
	@echo "  Ruff: $(shell ruff --version)"
	@echo "  Location: $(shell pwd)"

# Environment validation
validate-env:
	@echo "🔍 Validating environment..."
	@python -c "import sys; print(f'Python: {sys.version}')"
	@python -c "import nostr_tools; print(f'nostr-tools: {nostr_tools.__version__}')"
	@ruff --version
	@echo "✅ Environment validated"

# Quick development commands
quick-test: test-unit
quick-check: format-check lint test-unit
quick-fix: format lint-fix test-unit