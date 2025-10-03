"""
Unit tests for the exceptions module.

This module tests all custom exceptions including:
- RelayConnectionError creation and usage
- Exception inheritance
- Error message handling
"""

import pytest

from nostr_tools.exceptions import RelayConnectionError

# ============================================================================
# RelayConnectionError Tests
# ============================================================================


@pytest.mark.unit
class TestRelayConnectionError:
    """Test RelayConnectionError exception."""

    def test_create_relay_connection_error(self) -> None:
        """Test creating RelayConnectionError."""
        error = RelayConnectionError("Test error")
        assert isinstance(error, RelayConnectionError)
        assert isinstance(error, Exception)

    def test_relay_connection_error_message(self) -> None:
        """Test RelayConnectionError message."""
        message = "Failed to connect to relay"
        error = RelayConnectionError(message)
        assert str(error) == message

    def test_raise_relay_connection_error(self) -> None:
        """Test raising RelayConnectionError."""
        with pytest.raises(RelayConnectionError, match="Test error"):
            raise RelayConnectionError("Test error")

    def test_relay_connection_error_is_exception(self) -> None:
        """Test that RelayConnectionError is an Exception."""
        error = RelayConnectionError("Test")
        assert isinstance(error, BaseException)
        assert isinstance(error, Exception)

    def test_relay_connection_error_with_empty_message(self) -> None:
        """Test RelayConnectionError with empty message."""
        error = RelayConnectionError("")
        assert str(error) == ""

    def test_relay_connection_error_with_long_message(self) -> None:
        """Test RelayConnectionError with long message."""
        message = "A" * 1000
        error = RelayConnectionError(message)
        assert str(error) == message

    def test_relay_connection_error_with_unicode(self) -> None:
        """Test RelayConnectionError with Unicode message."""
        message = "连接失败 🚫"
        error = RelayConnectionError(message)
        assert str(error) == message

    def test_catch_relay_connection_error(self) -> None:
        """Test catching RelayConnectionError."""
        try:
            raise RelayConnectionError("Connection failed")
        except RelayConnectionError as e:
            assert "Connection failed" in str(e)

    def test_catch_as_base_exception(self) -> None:
        """Test catching RelayConnectionError as Exception."""
        try:
            raise RelayConnectionError("Error")
        except Exception as e:
            assert isinstance(e, RelayConnectionError)

    def test_error_with_formatted_message(self) -> None:
        """Test RelayConnectionError with formatted message."""
        relay_url = "wss://relay.example.com"
        error_detail = "Connection timeout"
        message = f"Failed to connect to {relay_url}: {error_detail}"
        error = RelayConnectionError(message)
        assert relay_url in str(error)
        assert error_detail in str(error)
