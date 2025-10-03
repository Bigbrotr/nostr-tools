"""
Test package for nostr-tools library.

This package contains unit tests and integration tests for the
nostr-tools library components.

Test Structure:
- test_basic.py: Core functionality tests (events, keys, relays, filters)
- test_integration.py: Integration tests with real relays (if added)
- test_performance.py: Performance and benchmark tests (if added)
- conftest.py: Pytest configuration and fixtures (if added)

Test Categories:
- Unit tests: Test individual components in isolation
- Integration tests: Test components working together
- Performance tests: Benchmark critical operations
- Cryptographic tests: Test cryptographic operations and edge cases

Usage:
    python -m pytest                    # Run all tests
    python -m pytest tests/test_basic.py # Run specific test file
    python -m pytest -v                 # Verbose output
    python -m pytest --cov=nostr_tools  # With coverage

Test Markers:
- unit: Unit tests (fast, no external dependencies)
- integration: Integration tests (may require network access)
- slow: Slow tests (proof-of-work, network operations)
- benchmark: Performance benchmark tests

Example Usage:
    # Run only unit tests
    python -m pytest -m unit

    # Skip slow tests
    python -m pytest -m "not slow"

    # Run benchmarks
    python -m pytest -m benchmark

    # Run with coverage
    python -m pytest --cov=nostr_tools --cov-report=html

Requirements:
- pytest>=7.0.0
- pytest-asyncio>=0.21.0
- pytest-cov>=4.0.0 (for coverage)
- pytest-mock>=3.10.0 (for mocking)

Environment Variables:
- NOSTR_TEST_RELAY: Override default test relay URL
- NOSTR_TEST_TIMEOUT: Override default test timeout
- NOSTR_SKIP_INTEGRATION: Skip integration tests
"""

import os

# Test configuration
TEST_RELAY_URL = os.getenv("NOSTR_TEST_RELAY", "wss://relay.damus.io")
TEST_TIMEOUT = int(os.getenv("NOSTR_TEST_TIMEOUT", "30"))
SKIP_INTEGRATION = os.getenv("NOSTR_SKIP_INTEGRATION", "false").lower() == "true"

# Common test fixtures and utilities can be imported here
# when added to conftest.py

__all__ = [
    "SKIP_INTEGRATION",
    "TEST_RELAY_URL",
    "TEST_TIMEOUT",
]
