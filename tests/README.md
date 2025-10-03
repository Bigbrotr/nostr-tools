# Nostr-Tools Test Suite

## Overview

This is a comprehensive, professional test suite for the nostr-tools Python package. The tests are organized by module and provide maximum code coverage with easy maintenance and extensibility.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (isolated, no external dependencies)
│   ├── test_event.py        # Event class tests
│   ├── test_filter.py       # Filter class tests
│   ├── test_relay.py        # Relay class tests
│   ├── test_client.py       # Client class tests
│   ├── test_relay_metadata.py  # RelayMetadata, Nip11, Nip66 tests
│   ├── test_utils.py        # Utility functions tests
│   └── test_exceptions.py   # Exception classes tests
├── integration/             # Integration tests (may require network)
│   └── test_actions.py      # High-level action functions tests
└── test_package.py          # Package-level tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Unit Tests Only
```bash
pytest tests/unit/ -m unit
```

### Run Integration Tests Only
```bash
pytest tests/integration/ -m integration
```

### Run With Coverage
```bash
pytest tests/ --cov=nostr_tools --cov-report=html --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/unit/test_event.py -v
```

### Run Specific Test Class or Function
```bash
pytest tests/unit/test_event.py::TestEventCreation::test_create_valid_event -v
```

## Test Categories

### Unit Tests (`tests/unit/`)

**test_event.py** - Event Class Tests
- Event creation and validation
- Type checking
- Signature verification
- Event ID calculation
- Dictionary conversion
- Edge cases (Unicode, empty content, max values, etc.)

**test_filter.py** - Filter Class Tests
- Filter creation with various parameters
- Validation rules
- Tag filtering
- Subscription filter generation
- Normalization logic

**test_relay.py** - Relay Class Tests
- Relay creation for clearnet and Tor
- URL validation
- Network type detection
- Dictionary conversion

**test_client.py** - Client Class Tests
- Client creation and configuration
- Connection management (mocked)
- Message sending
- Subscription management
- Event publishing
- Async context manager

**test_relay_metadata.py** - RelayMetadata Tests
- RelayMetadata creation
- Nip11 (relay information) validation
- Nip66 (connection metrics) validation
- Nested dataclass validation

**test_utils.py** - Utility Functions Tests
- WebSocket URL discovery
- Data sanitization
- Cryptographic operations (signing, verification)
- Event ID calculation
- Bech32 encoding/decoding
- Keypair generation and validation
- Proof-of-work mining

**test_exceptions.py** - Exception Tests
- RelayConnectionError creation and usage
- Exception inheritance

### Integration Tests (`tests/integration/`)

**test_actions.py** - Action Functions Tests
- fetch_events with mocked connections
- stream_events functionality
- fetch_nip11 with mocked HTTP
- Connectivity checks
- Relay metadata fetching

### Package Tests (`test_package.py`)

- Package imports
- Public API availability
- Lazy loading functionality
- Module structure
- Package metadata

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may require network)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.asyncio` - Async tests

## Fixtures

Common fixtures are defined in `conftest.py`:

### Data Fixtures
- `valid_keypair` - Generate a valid keypair
- `valid_private_key` - Valid private key
- `valid_public_key` - Valid public key
- `valid_event_dict` - Valid event dictionary
- `valid_event` - Valid Event instance
- `valid_filter_dict` - Valid filter dictionary
- `valid_filter` - Valid Filter instance
- `valid_relay_url` - Valid relay URL
- `valid_relay` - Valid Relay instance
- `tor_relay` - Tor Relay instance
- `valid_client` - Valid Client instance
- `tor_client` - Tor Client instance

### Mock Fixtures
- `mock_websocket` - Mocked WebSocket connection
- `mock_session` - Mocked aiohttp session

## Code Coverage

Current coverage: **83%**

Coverage breakdown by module:
- `core/event.py` - 100%
- `exceptions/errors.py` - 100%
- `core/filter.py` - 98%
- `core/relay.py` - 97%
- `utils/utils.py` - 93%
- `core/relay_metadata.py` - 92%
- `actions/actions.py` - 76%
- `core/client.py` - 62% (async/network code is harder to test)

## Adding New Tests

### For New Features

1. **Unit Tests**: Add to appropriate file in `tests/unit/`
   ```python
   @pytest.mark.unit
   class TestNewFeature:
       def test_feature_works(self):
           # Test implementation
           pass
   ```

2. **Integration Tests**: Add to `tests/integration/test_actions.py`
   ```python
   @pytest.mark.integration
   @pytest.mark.asyncio
   async def test_new_action(self):
       # Test implementation
       pass
   ```

### For New Modules

1. Create new test file: `tests/unit/test_newmodule.py`
2. Import the module and create test classes
3. Add fixtures to `conftest.py` if needed
4. Run tests and verify coverage

## Continuous Integration

Tests are configured to run in CI with:
- Multiple Python versions (3.9, 3.10, 3.11, 3.12, 3.13)
- Coverage reporting
- Strict markers and configuration
- Minimum coverage requirement: 80%

## Best Practices

1. **Isolation**: Unit tests should be isolated and not depend on external services
2. **Mocking**: Use mocks for external dependencies (network, filesystem)
3. **Fixtures**: Reuse fixtures from conftest.py
4. **Naming**: Use descriptive test names that explain what is being tested
5. **Organization**: Group related tests in classes
6. **Documentation**: Add docstrings to test functions
7. **Edge Cases**: Test edge cases and error conditions
8. **Coverage**: Aim for >80% coverage, focusing on critical paths

## Troubleshooting

### Import Errors
- Ensure the package is installed: `pip install -e .`
- Check virtual environment is activated

### Async Test Failures
- Ensure pytest-asyncio is installed
- Use `@pytest.mark.asyncio` decorator
- Check event loop configuration

### Coverage Issues
- Run with `--cov-report=html` for detailed report
- Check `htmlcov/index.html` in browser
- Focus on missing branches and lines

### Test Timeouts
- Use `@pytest.mark.timeout(seconds)` for long-running tests
- Increase timeout in pytest.ini if needed

## Maintenance

### Regular Tasks
1. Update fixtures when data structures change
2. Add tests for new features before merging
3. Keep coverage above 80%
4. Remove obsolete tests
5. Update mocks when external APIs change

### Test Health Checks
```bash
# Run fast tests
pytest tests/unit/ -v

# Check coverage
pytest tests/ --cov=nostr_tools --cov-report=term-missing

# Run with warnings
pytest tests/ -v -W error

# Profile slow tests
pytest tests/ --durations=10
```

## Contributing

When contributing tests:
1. Follow the existing structure and naming conventions
2. Add appropriate markers
3. Include docstrings
4. Ensure tests pass locally
5. Check coverage doesn't decrease
6. Update this README if adding new test categories
