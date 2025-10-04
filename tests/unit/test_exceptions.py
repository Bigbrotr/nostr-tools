"""
Unit tests for the exceptions module.

This module tests all custom Core exceptions including:
- NostrToolsError (base exception)
- ClientConnectionError
- EventValidationError
- FilterValidationError
- RelayValidationError
- ClientSubscriptionError
- ClientPublicationError
- Exception inheritance
- Error message handling
"""

import pytest

from nostr_tools.exceptions import ClientConnectionError
from nostr_tools.exceptions import ClientError
from nostr_tools.exceptions import ClientPublicationError
from nostr_tools.exceptions import ClientSubscriptionError
from nostr_tools.exceptions import ClientValidationError
from nostr_tools.exceptions import EventValidationError
from nostr_tools.exceptions import FilterValidationError
from nostr_tools.exceptions import Nip11Error
from nostr_tools.exceptions import Nip11ValidationError
from nostr_tools.exceptions import Nip66Error
from nostr_tools.exceptions import Nip66ValidationError
from nostr_tools.exceptions import NostrToolsError
from nostr_tools.exceptions import RelayMetadataError
from nostr_tools.exceptions import RelayMetadataValidationError
from nostr_tools.exceptions import RelayValidationError

# ============================================================================
# NostrToolsError (Base Exception) Tests
# ============================================================================


@pytest.mark.unit
class TestNostrToolsError:
    """Test NostrToolsError base exception."""

    def test_create_nostr_tools_error(self) -> None:
        """Test creating NostrToolsError."""
        error = NostrToolsError("Base error")
        assert isinstance(error, NostrToolsError)
        assert isinstance(error, Exception)

    def test_nostr_tools_error_message(self) -> None:
        """Test NostrToolsError message."""
        message = "Something went wrong"
        error = NostrToolsError(message)
        assert str(error) == message

    def test_raise_nostr_tools_error(self) -> None:
        """Test raising NostrToolsError."""
        with pytest.raises(NostrToolsError, match="Base error"):
            raise NostrToolsError("Base error")

    def test_catch_derived_as_base(self) -> None:
        """Test catching derived exception as NostrToolsError."""
        try:
            raise ClientConnectionError("Connection failed")
        except NostrToolsError as e:
            assert isinstance(e, ClientConnectionError)
            assert isinstance(e, NostrToolsError)


# ============================================================================
# ClientConnectionError Tests
# ============================================================================


@pytest.mark.unit
class TestClientConnectionError:
    """Test ClientConnectionError exception."""

    def test_create_client_connection_error(self) -> None:
        """Test creating ClientConnectionError."""
        error = ClientConnectionError("Test error")
        assert isinstance(error, ClientConnectionError)
        assert isinstance(error, ClientError)
        assert isinstance(error, NostrToolsError)
        assert isinstance(error, Exception)

    def test_client_connection_error_message(self) -> None:
        """Test ClientConnectionError message."""
        message = "Failed to connect to relay"
        error = ClientConnectionError(message)
        assert str(error) == message

    def test_raise_client_connection_error(self) -> None:
        """Test raising ClientConnectionError."""
        with pytest.raises(ClientConnectionError, match="Test error"):
            raise ClientConnectionError("Test error")

    def test_client_connection_error_is_exception(self) -> None:
        """Test that ClientConnectionError is an Exception."""
        error = ClientConnectionError("Test")
        assert isinstance(error, BaseException)
        assert isinstance(error, Exception)
        assert isinstance(error, NostrToolsError)

    def test_client_connection_error_with_empty_message(self) -> None:
        """Test ClientConnectionError with empty message."""
        error = ClientConnectionError("")
        assert str(error) == ""

    def test_client_connection_error_with_long_message(self) -> None:
        """Test ClientConnectionError with long message."""
        message = "A" * 1000
        error = ClientConnectionError(message)
        assert str(error) == message

    def test_client_connection_error_with_unicode(self) -> None:
        """Test ClientConnectionError with Unicode message."""
        message = "连接失败 🚫"
        error = ClientConnectionError(message)
        assert str(error) == message

    def test_catch_client_connection_error(self) -> None:
        """Test catching ClientConnectionError."""
        try:
            raise ClientConnectionError("Connection failed")
        except ClientConnectionError as e:
            assert "Connection failed" in str(e)

    def test_catch_as_base_exception(self) -> None:
        """Test catching ClientConnectionError as Exception."""
        try:
            raise ClientConnectionError("Error")
        except Exception as e:
            assert isinstance(e, ClientConnectionError)

    def test_error_with_formatted_message(self) -> None:
        """Test ClientConnectionError with formatted message."""
        relay_url = "wss://relay.example.com"
        error_detail = "Connection timeout"
        message = f"Failed to connect to {relay_url}: {error_detail}"
        error = ClientConnectionError(message)
        assert relay_url in str(error)
        assert error_detail in str(error)


# ============================================================================
# EventValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestEventValidationError:
    """Test EventValidationError exception."""

    def test_create_event_validation_error(self) -> None:
        """Test creating EventValidationError."""
        error = EventValidationError("Invalid event")
        assert isinstance(error, EventValidationError)
        assert isinstance(error, NostrToolsError)

    def test_event_validation_error_message(self) -> None:
        """Test EventValidationError message."""
        message = "Event signature is invalid"
        error = EventValidationError(message)
        assert str(error) == message

    def test_raise_event_validation_error(self) -> None:
        """Test raising EventValidationError."""
        with pytest.raises(EventValidationError, match="Invalid signature"):
            raise EventValidationError("Invalid signature")

    def test_catch_as_nostr_tools_error(self) -> None:
        """Test catching EventValidationError as NostrToolsError."""
        try:
            raise EventValidationError("Event validation failed")
        except NostrToolsError as e:
            assert isinstance(e, EventValidationError)


# ============================================================================
# FilterValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestFilterValidationError:
    """Test FilterValidationError exception."""

    def test_create_filter_validation_error(self) -> None:
        """Test creating FilterValidationError."""
        error = FilterValidationError("Invalid filter")
        assert isinstance(error, FilterValidationError)
        assert isinstance(error, NostrToolsError)

    def test_filter_validation_error_message(self) -> None:
        """Test FilterValidationError message."""
        message = "Filter limit must be positive"
        error = FilterValidationError(message)
        assert str(error) == message

    def test_raise_filter_validation_error(self) -> None:
        """Test raising FilterValidationError."""
        with pytest.raises(FilterValidationError, match="Invalid filter"):
            raise FilterValidationError("Invalid filter")

    def test_catch_as_nostr_tools_error(self) -> None:
        """Test catching FilterValidationError as NostrToolsError."""
        try:
            raise FilterValidationError("Filter validation failed")
        except NostrToolsError as e:
            assert isinstance(e, FilterValidationError)


# ============================================================================
# RelayValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestRelayValidationError:
    """Test RelayValidationError exception."""

    def test_create_relay_validation_error(self) -> None:
        """Test creating RelayValidationError."""
        error = RelayValidationError("Invalid relay")
        assert isinstance(error, RelayValidationError)
        assert isinstance(error, NostrToolsError)

    def test_relay_validation_error_message(self) -> None:
        """Test RelayValidationError message."""
        message = "Relay URL must be a valid WebSocket URL"
        error = RelayValidationError(message)
        assert str(error) == message

    def test_raise_relay_validation_error(self) -> None:
        """Test raising RelayValidationError."""
        with pytest.raises(RelayValidationError, match="Invalid URL"):
            raise RelayValidationError("Invalid URL")

    def test_catch_as_nostr_tools_error(self) -> None:
        """Test catching RelayValidationError as NostrToolsError."""
        try:
            raise RelayValidationError("Relay validation failed")
        except NostrToolsError as e:
            assert isinstance(e, RelayValidationError)


# ============================================================================
# ClientSubscriptionError Tests
# ============================================================================


@pytest.mark.unit
class TestClientSubscriptionError:
    """Test ClientSubscriptionError exception."""

    def test_create_client_subscription_error(self) -> None:
        """Test creating ClientSubscriptionError."""
        error = ClientSubscriptionError("Subscription failed")
        assert isinstance(error, ClientSubscriptionError)
        assert isinstance(error, ClientError)
        assert isinstance(error, NostrToolsError)

    def test_client_subscription_error_message(self) -> None:
        """Test ClientSubscriptionError message."""
        message = "Subscription not found: sub_123"
        error = ClientSubscriptionError(message)
        assert str(error) == message

    def test_raise_client_subscription_error(self) -> None:
        """Test raising ClientSubscriptionError."""
        with pytest.raises(ClientSubscriptionError, match="Subscription failed"):
            raise ClientSubscriptionError("Subscription failed")

    def test_catch_as_nostr_tools_error(self) -> None:
        """Test catching ClientSubscriptionError as NostrToolsError."""
        try:
            raise ClientSubscriptionError("Subscription error")
        except NostrToolsError as e:
            assert isinstance(e, ClientSubscriptionError)

    def test_client_subscription_error_with_sub_id(self) -> None:
        """Test ClientSubscriptionError with subscription ID."""
        sub_id = "test-sub-123"
        error = ClientSubscriptionError(f"Subscription '{sub_id}' not found")
        assert sub_id in str(error)


# ============================================================================
# ClientPublicationError Tests
# ============================================================================


@pytest.mark.unit
class TestClientPublicationError:
    """Test ClientPublicationError exception."""

    def test_create_client_publication_error(self) -> None:
        """Test creating ClientPublicationError."""
        error = ClientPublicationError("Publish failed")
        assert isinstance(error, ClientPublicationError)
        assert isinstance(error, ClientError)
        assert isinstance(error, NostrToolsError)

    def test_client_publication_error_message(self) -> None:
        """Test ClientPublicationError message."""
        message = "Relay rejected event: spam"
        error = ClientPublicationError(message)
        assert str(error) == message

    def test_raise_client_publication_error(self) -> None:
        """Test raising ClientPublicationError."""
        with pytest.raises(ClientPublicationError, match="Publish failed"):
            raise ClientPublicationError("Publish failed")

    def test_catch_as_nostr_tools_error(self) -> None:
        """Test catching ClientPublicationError as NostrToolsError."""
        try:
            raise ClientPublicationError("Publish error")
        except NostrToolsError as e:
            assert isinstance(e, ClientPublicationError)

    def test_client_publication_error_with_reason(self) -> None:
        """Test ClientPublicationError with rejection reason."""
        reason = "insufficient proof of work"
        error = ClientPublicationError(f"Relay rejected event: {reason}")
        assert reason in str(error)


# ============================================================================
# Exception Hierarchy Tests
# ============================================================================


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self) -> None:
        """Test that all custom exceptions inherit from NostrToolsError."""
        exceptions = [
            ClientConnectionError,
            EventValidationError,
            FilterValidationError,
            RelayValidationError,
            ClientSubscriptionError,
            ClientPublicationError,
        ]

        for exc_class in exceptions:
            error = exc_class("Test")
            assert isinstance(error, NostrToolsError)
            assert isinstance(error, Exception)

    def test_catch_all_with_base_exception(self) -> None:
        """Test catching all custom exceptions with NostrToolsError."""
        errors_caught = []

        exceptions_to_raise = [
            ClientConnectionError("conn"),
            EventValidationError("event"),
            FilterValidationError("filter"),
            RelayValidationError("relay"),
            ClientSubscriptionError("sub"),
            ClientPublicationError("publish"),
        ]

        for exc in exceptions_to_raise:
            try:
                raise exc
            except NostrToolsError as e:
                errors_caught.append(e)

        assert len(errors_caught) == len(exceptions_to_raise)

    def test_exception_types_are_distinct(self) -> None:
        """Test that each exception type is distinct."""
        exceptions = [
            ClientConnectionError("test"),
            EventValidationError("test"),
            FilterValidationError("test"),
            RelayValidationError("test"),
            ClientSubscriptionError("test"),
            ClientPublicationError("test"),
        ]

        # Each exception should only be an instance of its own type
        for i, exc1 in enumerate(exceptions):
            for j, exc2 in enumerate(exceptions):
                if i == j:
                    assert isinstance(exc1, type(exc2))
                else:
                    assert not isinstance(exc1, type(exc2))


# ============================================================================
# ClientValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestClientValidationError:
    """Test ClientValidationError exception."""

    def test_create_client_validation_error(self) -> None:
        """Test creating ClientValidationError."""
        error = ClientValidationError("timeout must be non-negative")
        assert isinstance(error, ClientValidationError)
        assert isinstance(error, NostrToolsError)

    def test_raise_client_validation_error(self) -> None:
        """Test raising ClientValidationError."""
        with pytest.raises(ClientValidationError, match="timeout must be non-negative"):
            raise ClientValidationError("timeout must be non-negative")


# ============================================================================
# RelayMetadataValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestRelayMetadataValidationError:
    """Test RelayMetadataValidationError exception."""

    def test_create_relay_metadata_validation_error(self) -> None:
        """Test creating RelayMetadataValidationError."""
        error = RelayMetadataValidationError("generated_at must be non-negative")
        assert isinstance(error, RelayMetadataValidationError)
        assert isinstance(error, NostrToolsError)

    def test_raise_relay_metadata_validation_error(self) -> None:
        """Test raising RelayMetadataValidationError."""
        with pytest.raises(RelayMetadataValidationError, match="generated_at must be non-negative"):
            raise RelayMetadataValidationError("generated_at must be non-negative")


# ============================================================================
# Nip11ValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestNip11ValidationError:
    """Test Nip11ValidationError exception."""

    def test_create_nip11_validation_error(self) -> None:
        """Test creating Nip11ValidationError."""
        error = Nip11ValidationError("supported_nips must be a list")
        assert isinstance(error, Nip11ValidationError)
        assert isinstance(error, NostrToolsError)

    def test_raise_nip11_validation_error(self) -> None:
        """Test raising Nip11ValidationError."""
        with pytest.raises(Nip11ValidationError, match="supported_nips must be a list"):
            raise Nip11ValidationError("supported_nips must be a list")


# ============================================================================
# Nip66ValidationError Tests
# ============================================================================


@pytest.mark.unit
class TestNip66ValidationError:
    """Test Nip66ValidationError exception."""

    def test_create_nip66_validation_error(self) -> None:
        """Test creating Nip66ValidationError."""
        error = Nip66ValidationError("rtt_open must be provided when openable is True")
        assert isinstance(error, Nip66ValidationError)
        assert isinstance(error, NostrToolsError)

    def test_raise_nip66_validation_error(self) -> None:
        """Test raising Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="rtt_open must be provided"):
            raise Nip66ValidationError("rtt_open must be provided when openable is True")


# ============================================================================
# Nip11Error Tests
# ============================================================================


@pytest.mark.unit
class TestNip11Error:
    """Test Nip11Error exception."""

    def test_create_nip11_error(self) -> None:
        """Test creating Nip11Error."""
        error = Nip11Error("NIP-11 error")
        assert isinstance(error, Nip11Error)
        assert isinstance(error, RelayMetadataError)
        assert isinstance(error, NostrToolsError)

    def test_raise_nip11_error(self) -> None:
        """Test raising Nip11Error."""
        with pytest.raises(Nip11Error, match="NIP-11 error"):
            raise Nip11Error("NIP-11 error")


# ============================================================================
# Nip66Error Tests
# ============================================================================


@pytest.mark.unit
class TestNip66Error:
    """Test Nip66Error exception."""

    def test_create_nip66_error(self) -> None:
        """Test creating Nip66Error."""
        error = Nip66Error("NIP-66 error")
        assert isinstance(error, Nip66Error)
        assert isinstance(error, RelayMetadataError)
        assert isinstance(error, NostrToolsError)

    def test_raise_nip66_error(self) -> None:
        """Test raising Nip66Error."""
        with pytest.raises(Nip66Error, match="NIP-66 error"):
            raise Nip66Error("NIP-66 error")
