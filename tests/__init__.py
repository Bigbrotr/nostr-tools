"""
Test package for nostr-tools library.

This package contains unit tests for the nostr-tools library components.

Test Structure:
- unit/: Unit tests for individual components
  - test_client.py: Client functionality tests
  - test_event.py: Event creation and validation tests
  - test_filter.py: Filter creation and validation tests
  - test_relay.py: Relay validation tests
  - test_relay_metadata.py: Relay metadata tests
  - test_utils.py: Utility function tests
  - test_actions.py: High-level action function tests
  - test_exceptions.py: Exception handling tests
  - test_coverage_boost.py: Additional coverage tests
- test_package.py: Package structure and import tests
- conftest.py: Pytest configuration and shared fixtures

Test Categories:
- Unit tests: Test individual components in isolation with mocking

Usage:
    make test              # Run all tests with coverage
    make test-unit         # Run unit tests only
    make test-cov          # Generate HTML coverage report
    make test-quick        # Quick test run without coverage

Or directly with pytest:
    python -m pytest                    # Run all tests
    python -m pytest tests/unit/        # Run unit tests only
    python -m pytest -v                 # Verbose output
    python -m pytest --cov=nostr_tools  # With coverage

Test Markers:
- unit: Unit tests (fast, no external dependencies)

Example Usage:
    # Run only unit tests
    python -m pytest -m unit

    # Run with coverage report
    python -m pytest --cov=nostr_tools --cov-report=html

Requirements:
- pytest>=7.4.0
- pytest-asyncio>=0.23.0
- pytest-cov>=4.0.0
- pytest-mock>=3.12.0
"""

# Common test fixtures and utilities are imported from conftest.py

__all__: list[str] = []
