"""
Unit tests for the RelayMetadata, Nip11, and Nip66 classes.

This module tests all functionality of the RelayMetadata module including:
- RelayMetadata creation and validation
- Nip11 (relay information) validation
- Nip66 (connection metrics) validation
- Dictionary conversion
- Edge cases and error handling
"""

import time
from typing import Any

import pytest

from nostr_tools.core.relay import Relay
from nostr_tools.core.relay_metadata import RelayMetadata
from nostr_tools.exceptions import Nip11ValidationError
from nostr_tools.exceptions import Nip66ValidationError
from nostr_tools.exceptions import RelayMetadataValidationError

# ============================================================================
# Nip11 Creation Tests
# ============================================================================


@pytest.mark.unit
class TestNip11Creation:
    """Test Nip11 instance creation."""

    def test_create_empty_nip11(self) -> None:
        """Test creating an empty Nip11."""
        nip11 = RelayMetadata.Nip11()
        assert isinstance(nip11, RelayMetadata.Nip11)
        assert nip11.name is None
        assert nip11.description is None

    def test_create_nip11_with_basic_fields(self) -> None:
        """Test creating Nip11 with basic fields."""
        nip11 = RelayMetadata.Nip11(
            name="Test Relay", description="A test relay", contact="test@example.com"
        )
        assert nip11.name == "Test Relay"
        assert nip11.description == "A test relay"
        assert nip11.contact == "test@example.com"

    def test_create_nip11_with_all_fields(self) -> None:
        """Test creating Nip11 with all fields."""
        nip11 = RelayMetadata.Nip11(
            name="Test Relay",
            description="Description",
            banner="https://example.com/banner.jpg",
            icon="https://example.com/icon.png",
            pubkey="a" * 64,
            contact="test@example.com",
            supported_nips=[1, 2, 11],
            software="nostr-relay",
            version="1.0.0",
            privacy_policy="https://example.com/privacy",
            terms_of_service="https://example.com/terms",
            limitation={"max_message_length": 16384},
            extra_fields={"custom_field": "value"},
        )
        assert nip11.supported_nips == [1, 2, 11]
        assert nip11.limitation == {"max_message_length": 16384}


# ============================================================================
# Nip11 Validation Tests
# ============================================================================


@pytest.mark.unit
class TestNip11Validation:
    """Test Nip11 validation logic."""

    def test_valid_nip11_passes_validation(self, valid_nip11_dict: dict[str, Any]) -> None:
        """Test that valid Nip11 passes validation."""
        nip11 = RelayMetadata.Nip11.from_dict(valid_nip11_dict)
        nip11.validate()  # Should not raise
        assert nip11.is_valid

    def test_empty_supported_nips_normalized_to_none(self) -> None:
        """Test that empty supported_nips is normalized to None."""
        # Empty lists are normalized to None in __post_init__
        nip11 = RelayMetadata.Nip11(supported_nips=[])
        assert nip11.supported_nips is None

    def test_empty_limitation_normalized_to_none(self) -> None:
        """Test that empty limitation is normalized to None."""
        # Empty dicts are normalized to None in __post_init__
        nip11 = RelayMetadata.Nip11(limitation={})
        assert nip11.limitation is None

    def test_empty_extra_fields_normalized_to_none(self) -> None:
        """Test that empty extra_fields is normalized to None."""
        # Empty dicts are normalized to None in __post_init__
        nip11 = RelayMetadata.Nip11(extra_fields={})
        assert nip11.extra_fields is None

    def test_non_json_serializable_limitation_raises_error(self) -> None:
        """Test that non-JSON serializable limitation raises Nip11ValidationError."""

        # Create an object that can't be JSON serialized
        class NonSerializable:
            pass

        with pytest.raises(Nip11ValidationError, match="must be JSON serializable"):
            RelayMetadata.Nip11(limitation={"obj": NonSerializable()})

    def test_non_json_serializable_extra_fields_raises_error(self) -> None:
        """Test that non-JSON serializable extra_fields raises Nip11ValidationError."""

        class NonSerializable:
            pass

        with pytest.raises(Nip11ValidationError, match="must be JSON serializable"):
            RelayMetadata.Nip11(extra_fields={"obj": NonSerializable()})

    def test_non_string_keys_in_limitation_raises_error(self) -> None:
        """Test that non-string keys in limitation raise Nip11ValidationError."""
        with pytest.raises(Nip11ValidationError, match="All keys .* must be strings"):
            RelayMetadata.Nip11(limitation={1: "value"})  # type: ignore

    def test_non_string_keys_in_extra_fields_raises_error(self) -> None:
        """Test that non-string keys in extra_fields raise Nip11ValidationError."""
        with pytest.raises(Nip11ValidationError, match="All keys .* must be strings"):
            RelayMetadata.Nip11(extra_fields={1: "value"})  # type: ignore


# ============================================================================
# Nip11 Type Validation Tests
# ============================================================================


@pytest.mark.unit
class TestNip11TypeValidation:
    """Test Nip11 type validation."""

    def test_non_string_name_raises_error(self) -> None:
        """Test that non-string name raises Nip11ValidationError."""
        with pytest.raises(Nip11ValidationError, match="name must be"):
            RelayMetadata.Nip11(name=123)  # type: ignore

    def test_non_string_description_raises_error(self) -> None:
        """Test that non-string description raises Nip11ValidationError."""
        with pytest.raises(Nip11ValidationError, match="description must be"):
            RelayMetadata.Nip11(description=123)  # type: ignore

    def test_non_list_supported_nips_raises_error(self) -> None:
        """Test that non-list supported_nips raises Nip11ValidationError."""
        with pytest.raises(Nip11ValidationError, match="supported_nips must be"):
            RelayMetadata.Nip11(supported_nips="not_a_list")  # type: ignore

    def test_invalid_supported_nips_element_type_raises_error(self) -> None:
        """Test that invalid element type in supported_nips raises Nip11ValidationError."""
        # Only int or str are allowed
        with pytest.raises(Nip11ValidationError, match="supported_nips must be"):
            RelayMetadata.Nip11(supported_nips=[{"invalid": "type"}])  # type: ignore


# ============================================================================
# Nip66 Creation Tests
# ============================================================================


@pytest.mark.unit
class TestNip66Creation:
    """Test Nip66 instance creation."""

    def test_create_default_nip66(self) -> None:
        """Test creating Nip66 with defaults."""
        nip66 = RelayMetadata.Nip66()
        assert nip66.openable is False
        assert nip66.readable is False
        assert nip66.writable is False
        assert nip66.rtt_open is None
        assert nip66.rtt_read is None
        assert nip66.rtt_write is None

    def test_create_nip66_openable_only(self) -> None:
        """Test creating Nip66 with only openable."""
        nip66 = RelayMetadata.Nip66(openable=True, rtt_open=100)
        assert nip66.openable is True
        assert nip66.rtt_open == 100

    def test_create_nip66_fully_functional(self) -> None:
        """Test creating fully functional Nip66."""
        nip66 = RelayMetadata.Nip66(
            openable=True,
            readable=True,
            writable=True,
            rtt_open=100,
            rtt_read=50,
            rtt_write=75,
        )
        assert nip66.openable is True
        assert nip66.readable is True
        assert nip66.writable is True


# ============================================================================
# Nip66 Validation Tests
# ============================================================================


@pytest.mark.unit
class TestNip66Validation:
    """Test Nip66 validation logic."""

    def test_valid_nip66_passes_validation(self, valid_nip66_dict: dict[str, Any]) -> None:
        """Test that valid Nip66 passes validation."""
        nip66 = RelayMetadata.Nip66.from_dict(valid_nip66_dict)
        nip66.validate()  # Should not raise
        assert nip66.is_valid

    def test_readable_without_openable_raises_error(self) -> None:
        """Test that readable without openable raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="openable must be True"):
            RelayMetadata.Nip66(readable=True, rtt_read=50)

    def test_writable_without_openable_raises_error(self) -> None:
        """Test that writable without openable raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="openable must be True"):
            RelayMetadata.Nip66(writable=True, rtt_write=75)

    def test_openable_without_rtt_raises_error(self) -> None:
        """Test that openable without rtt_open raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="rtt_open must be provided"):
            RelayMetadata.Nip66(openable=True)

    def test_readable_without_rtt_raises_error(self) -> None:
        """Test that readable without rtt_read raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="rtt_read must be provided"):
            RelayMetadata.Nip66(openable=True, rtt_open=100, readable=True)

    def test_writable_without_rtt_raises_error(self) -> None:
        """Test that writable without rtt_write raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="rtt_write must be provided"):
            RelayMetadata.Nip66(
                openable=True, rtt_open=100, readable=True, rtt_read=50, writable=True
            )

    def test_rtt_without_flag_raises_error(self) -> None:
        """Test that rtt without corresponding flag raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="rtt_open must be None"):
            RelayMetadata.Nip66(openable=False, rtt_open=100)

    def test_negative_rtt_raises_error(self) -> None:
        """Test that negative rtt raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="must be non-negative"):
            RelayMetadata.Nip66(openable=True, rtt_open=-1)


# ============================================================================
# Nip66 Type Validation Tests
# ============================================================================


@pytest.mark.unit
class TestNip66TypeValidation:
    """Test Nip66 type validation."""

    def test_non_bool_openable_raises_error(self) -> None:
        """Test that non-bool openable raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="openable must be"):
            RelayMetadata.Nip66(openable="not_a_bool")  # type: ignore

    def test_non_bool_readable_raises_error(self) -> None:
        """Test that non-bool readable raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="readable must be"):
            RelayMetadata.Nip66(readable="not_a_bool")  # type: ignore

    def test_non_bool_writable_raises_error(self) -> None:
        """Test that non-bool writable raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="writable must be"):
            RelayMetadata.Nip66(writable="not_a_bool")  # type: ignore

    def test_non_int_rtt_open_raises_error(self) -> None:
        """Test that non-int rtt_open raises Nip66ValidationError."""
        with pytest.raises(Nip66ValidationError, match="rtt_open must be"):
            RelayMetadata.Nip66(openable=True, rtt_open="not_an_int")  # type: ignore


# ============================================================================
# RelayMetadata Creation Tests
# ============================================================================


@pytest.mark.unit
class TestRelayMetadataCreation:
    """Test RelayMetadata instance creation."""

    def test_create_relay_metadata_minimal(self, valid_relay: Relay) -> None:
        """Test creating RelayMetadata with minimal data."""
        metadata = RelayMetadata(relay=valid_relay, generated_at=int(time.time()))
        assert isinstance(metadata, RelayMetadata)
        assert metadata.relay == valid_relay
        assert metadata.nip11 is None
        assert metadata.nip66 is None

    def test_create_relay_metadata_with_nip11(
        self, valid_relay: Relay, valid_nip11_dict: dict[str, Any]
    ) -> None:
        """Test creating RelayMetadata with Nip11."""
        nip11 = RelayMetadata.Nip11.from_dict(valid_nip11_dict)
        metadata = RelayMetadata(relay=valid_relay, nip11=nip11, generated_at=int(time.time()))
        assert metadata.nip11 == nip11

    def test_create_relay_metadata_with_nip66(
        self, valid_relay: Relay, valid_nip66_dict: dict[str, Any]
    ) -> None:
        """Test creating RelayMetadata with Nip66."""
        nip66 = RelayMetadata.Nip66.from_dict(valid_nip66_dict)
        metadata = RelayMetadata(relay=valid_relay, nip66=nip66, generated_at=int(time.time()))
        assert metadata.nip66 == nip66

    def test_create_relay_metadata_complete(
        self,
        valid_relay: Relay,
        valid_nip11_dict: dict[str, Any],
        valid_nip66_dict: dict[str, Any],
    ) -> None:
        """Test creating complete RelayMetadata."""
        nip11 = RelayMetadata.Nip11.from_dict(valid_nip11_dict)
        nip66 = RelayMetadata.Nip66.from_dict(valid_nip66_dict)
        generated_at = int(time.time())

        metadata = RelayMetadata(
            relay=valid_relay, nip11=nip11, nip66=nip66, generated_at=generated_at
        )
        assert metadata.relay == valid_relay
        assert metadata.nip11 == nip11
        assert metadata.nip66 == nip66
        assert metadata.generated_at == generated_at


# ============================================================================
# RelayMetadata Validation Tests
# ============================================================================


@pytest.mark.unit
class TestRelayMetadataValidation:
    """Test RelayMetadata validation logic."""

    def test_valid_relay_metadata_passes_validation(
        self, valid_relay_metadata_dict: dict[str, Any]
    ) -> None:
        """Test that valid RelayMetadata passes validation."""
        metadata = RelayMetadata.from_dict(valid_relay_metadata_dict)
        metadata.validate()  # Should not raise
        assert metadata.is_valid

    def test_negative_generated_at_raises_error(self, valid_relay: Relay) -> None:
        """Test that negative generated_at raises RelayMetadataValidationError."""
        with pytest.raises(RelayMetadataValidationError, match="generated_at must be non-negative"):
            RelayMetadata(relay=valid_relay, generated_at=-1)

    def test_non_relay_type_raises_error(self) -> None:
        """Test that non-Relay type raises RelayMetadataValidationError."""
        with pytest.raises(RelayMetadataValidationError, match="relay must be"):
            RelayMetadata(relay="not_a_relay", generated_at=int(time.time()))  # type: ignore

    def test_non_int_generated_at_raises_error(self, valid_relay: Relay) -> None:
        """Test that non-int generated_at raises RelayMetadataValidationError."""
        with pytest.raises(RelayMetadataValidationError, match="generated_at must be"):
            RelayMetadata(relay=valid_relay, generated_at="not_an_int")  # type: ignore


# ============================================================================
# RelayMetadata Dictionary Conversion Tests
# ============================================================================


@pytest.mark.unit
class TestRelayMetadataDictionaryConversion:
    """Test RelayMetadata dictionary conversion."""

    def test_from_dict_creates_relay_metadata(
        self, valid_relay_metadata_dict: dict[str, Any]
    ) -> None:
        """Test that from_dict creates RelayMetadata."""
        metadata = RelayMetadata.from_dict(valid_relay_metadata_dict)
        assert isinstance(metadata, RelayMetadata)

    def test_from_dict_with_non_dict_raises_error(self) -> None:
        """Test that from_dict with non-dict raises TypeError."""
        with pytest.raises(TypeError, match="data must be a dict"):
            RelayMetadata.from_dict("not_a_dict")  # type: ignore

    def test_to_dict_returns_dict(self, valid_relay_metadata_dict: dict[str, Any]) -> None:
        """Test that to_dict returns a dictionary."""
        metadata = RelayMetadata.from_dict(valid_relay_metadata_dict)
        metadata_dict = metadata.to_dict()
        assert isinstance(metadata_dict, dict)

    def test_to_dict_contains_all_fields(self, valid_relay_metadata_dict: dict[str, Any]) -> None:
        """Test that to_dict contains all fields."""
        metadata = RelayMetadata.from_dict(valid_relay_metadata_dict)
        metadata_dict = metadata.to_dict()
        assert "relay" in metadata_dict
        assert "nip11" in metadata_dict
        assert "nip66" in metadata_dict
        assert "generated_at" in metadata_dict

    def test_round_trip_conversion_relay_metadata(
        self, valid_relay_metadata_dict: dict[str, Any]
    ) -> None:
        """Test that RelayMetadata can be converted to dict and back."""
        metadata1 = RelayMetadata.from_dict(valid_relay_metadata_dict)
        metadata_dict = metadata1.to_dict()
        metadata2 = RelayMetadata.from_dict(metadata_dict)

        assert metadata1.relay.url == metadata2.relay.url
        assert metadata1.generated_at == metadata2.generated_at

    def test_nip11_round_trip_conversion(self, valid_nip11_dict: dict[str, Any]) -> None:
        """Test that Nip11 can be converted to dict and back."""
        nip11_1 = RelayMetadata.Nip11.from_dict(valid_nip11_dict)
        nip11_dict = nip11_1.to_dict()
        nip11_2 = RelayMetadata.Nip11.from_dict(nip11_dict)

        assert nip11_1.name == nip11_2.name
        assert nip11_1.supported_nips == nip11_2.supported_nips

    def test_nip66_round_trip_conversion(self, valid_nip66_dict: dict[str, Any]) -> None:
        """Test that Nip66 can be converted to dict and back."""
        nip66_1 = RelayMetadata.Nip66.from_dict(valid_nip66_dict)
        nip66_dict = nip66_1.to_dict()
        nip66_2 = RelayMetadata.Nip66.from_dict(nip66_dict)

        assert nip66_1.openable == nip66_2.openable
        assert nip66_1.readable == nip66_2.readable
        assert nip66_1.writable == nip66_2.writable


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.unit
class TestRelayMetadataEdgeCases:
    """Test RelayMetadata edge cases."""

    def test_nip11_with_string_supported_nips(self) -> None:
        """Test Nip11 with string NIPs (e.g., 'draft')."""
        nip11 = RelayMetadata.Nip11(supported_nips=[1, 2, "draft"])
        assert nip11.supported_nips == [1, 2, "draft"]

    def test_nip11_with_complex_limitation(self) -> None:
        """Test Nip11 with complex limitation structure."""
        limitation = {
            "max_message_length": 16384,
            "max_subscriptions": 20,
            "max_filters": 100,
            "max_limit": 5000,
            "max_subid_length": 100,
            "min_prefix": 4,
            "max_event_tags": 100,
            "max_content_length": 8196,
            "min_pow_difficulty": 30,
            "auth_required": True,
            "payment_required": False,
        }
        nip11 = RelayMetadata.Nip11(limitation=limitation)
        assert nip11.limitation == limitation

    def test_nip11_with_extra_fields(self) -> None:
        """Test Nip11 with extra custom fields."""
        extra = {"custom_field": "value", "nested": {"data": 123}}
        nip11 = RelayMetadata.Nip11(extra_fields=extra)
        assert nip11.extra_fields == extra

    def test_nip66_with_zero_rtt(self) -> None:
        """Test Nip66 with zero RTT values."""
        nip66 = RelayMetadata.Nip66(
            openable=True,
            readable=True,
            writable=True,
            rtt_open=0,
            rtt_read=0,
            rtt_write=0,
        )
        assert nip66.rtt_open == 0
        assert nip66.rtt_read == 0
        assert nip66.rtt_write == 0

    def test_nip66_with_very_high_rtt(self) -> None:
        """Test Nip66 with very high RTT values."""
        nip66 = RelayMetadata.Nip66(
            openable=True,
            rtt_open=999999,  # Very slow connection
        )
        assert nip66.rtt_open == 999999

    def test_relay_metadata_with_future_timestamp(self, valid_relay: Relay) -> None:
        """Test RelayMetadata with future timestamp."""
        future_time = int(time.time()) + 86400  # Tomorrow
        metadata = RelayMetadata(relay=valid_relay, generated_at=future_time)
        assert metadata.generated_at == future_time

    def test_relay_metadata_with_very_old_timestamp(self, valid_relay: Relay) -> None:
        """Test RelayMetadata with very old timestamp."""
        old_time = 1  # Unix epoch + 1 second
        metadata = RelayMetadata(relay=valid_relay, generated_at=old_time)
        assert metadata.generated_at == old_time


# ============================================================================
# Additional RelayMetadata Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestRelayMetadataAdditionalCoverage:
    """Additional tests for improved RelayMetadata coverage."""

    def test_nip11_with_none_values(self) -> None:
        """Test Nip11 with all None values."""
        nip11 = RelayMetadata.Nip11()
        assert nip11.name is None
        assert nip11.description is None
        assert nip11.is_valid is True

    def test_nip66_with_false_flags(self) -> None:
        """Test Nip66 with all flags False."""
        nip66 = RelayMetadata.Nip66(
            openable=False,
            readable=False,
            writable=False,
        )
        assert nip66.openable is False
        assert nip66.rtt_open is None
        assert nip66.rtt_read is None
        assert nip66.rtt_write is None

    def test_relay_metadata_minimal(self, valid_relay: Relay) -> None:
        """Test RelayMetadata with minimal data."""
        metadata = RelayMetadata(
            relay=valid_relay,
            generated_at=int(time.time()),
        )
        assert metadata.nip11 is None
        assert metadata.nip66 is None
        assert metadata.is_valid is True
