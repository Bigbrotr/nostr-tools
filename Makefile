.PHONY: help install install-dev test test-cov lint format clean build upload upload-test docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install       Install the package"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run linting (flake8, mypy)"
	@echo "  format        Format code (black, isort)"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  upload-test   Upload to Test PyPI"
	@echo "  upload        Upload to PyPI"
	@echo "  docs          Generate documentation"
	@echo "  check         Run all checks (format, lint, test)"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e .[dev]

# Testing
test:
	python -m pytest

test-cov:
	python -m pytest --cov=nostr_tools --cov-report=html --cov-report=term-missing

test-verbose:
	python -m pytest -v

# Code quality
lint:
	flake8 nostr_tools tests
	mypy nostr_tools

format:
	black nostr_tools tests examples
	isort nostr_tools tests examples

format-check:
	black --check nostr_tools tests examples
	isort --check-only nostr_tools tests examples

# Security
security:
	bandit -r nostr_tools
	safety check

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build
build: clean
	python -m build

# Upload
upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

# Documentation
docs:
	@echo "Documentation is in README.md"
	@echo "Run 'python examples/basic_usage.py' for live examples"

# Pre-commit setup
setup-hooks:
	pre-commit install

# Run all checks
check: format-check lint test

# Development workflow
dev-setup: install-dev setup-hooks
	@echo "Development environment ready!"

# Quick test for development
quick-test:
	python -m pytest tests/test_basic.py -v

# Run examples
run-examples:
	python examples/basic_usage.py

run-advanced:
	python examples/advanced_features.py

# Package verification
verify: build
	python -m twine check dist/*
	@echo "Package verification complete"

# Full release workflow
release-check: clean format-check lint test-cov security verify
	@echo "Release checks passed!"

# Local development server for documentation
serve-docs:
	@echo "Opening README.md for documentation"
	@echo "For live examples, run: make run-examples"