"""Nostr relay metadata representation."""

from typing import Optional, List, Dict, Any
from .relay import Relay
import json


class RelayMetadata:
    """
    Class to represent metadata associated with a NOSTR relay.

    This includes connection metrics, NIP-11 information document data,
    and operational capabilities.
    """

    def __init__(
        self,
        relay: Relay,
        generated_at: int,
        connection_success: bool = False,
        nip11_success: bool = False,
        openable: Optional[bool] = None,
        readable: Optional[bool] = None,
        writable: Optional[bool] = None,
        rtt_open: Optional[int] = None,
        rtt_read: Optional[int] = None,
        rtt_write: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        banner: Optional[str] = None,
        icon: Optional[str] = None,
        pubkey: Optional[str] = None,
        contact: Optional[str] = None,
        supported_nips: Optional[List[int]] = None,
        software: Optional[str] = None,
        version: Optional[str] = None,
        privacy_policy: Optional[str] = None,
        terms_of_service: Optional[str] = None,
        limitation: Optional[Dict[str, Any]] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a RelayMetadata object.

        Args:
            relay: The relay object
            generated_at: Timestamp when metadata was generated
            connection_success: Whether connection was successful
            nip11_success: Whether NIP-11 metadata was retrieved
            openable: Whether relay accepts connections
            readable: Whether relay allows reading
            writable: Whether relay allows writing
            rtt_open: Round-trip time for connection (ms)
            rtt_read: Round-trip time for reading (ms)
            rtt_write: Round-trip time for writing (ms)
            name: Relay name
            description: Relay description
            banner: Banner image URL
            icon: Icon image URL
            pubkey: Relay public key
            contact: Contact information
            supported_nips: List of supported NIPs
            software: Software name
            version: Software version
            privacy_policy: Privacy policy URL
            terms_of_service: Terms of service URL
            limitation: Relay limitations
            extra_fields: Additional custom fields
        """
        # Validate types
        if not isinstance(relay, Relay):
            raise TypeError(f"relay must be a Relay object, not {type(relay)}")
        if not isinstance(generated_at, int):
            raise TypeError(
                f"generated_at must be an int, not {type(generated_at)}")
        if not isinstance(connection_success, bool):
            raise TypeError(
                f"connection_success must be a bool, not {type(connection_success)}")
        if not isinstance(nip11_success, bool):
            raise TypeError(
                f"nip11_success must be a bool, not {type(nip11_success)}")

        # Validate optional fields
        self._validate_optional_field("openable", openable, bool)
        self._validate_optional_field("readable", readable, bool)
        self._validate_optional_field("writable", writable, bool)
        self._validate_optional_field("rtt_open", rtt_open, int)
        self._validate_optional_field("rtt_read", rtt_read, int)
        self._validate_optional_field("rtt_write", rtt_write, int)
        self._validate_optional_field("name", name, str)
        self._validate_optional_field("description", description, str)
        self._validate_optional_field("banner", banner, str)
        self._validate_optional_field("icon", icon, str)
        self._validate_optional_field("pubkey", pubkey, str)
        self._validate_optional_field("contact", contact, str)
        self._validate_optional_field("software", software, str)
        self._validate_optional_field("version", version, str)
        self._validate_optional_field("privacy_policy", privacy_policy, str)
        self._validate_optional_field(
            "terms_of_service", terms_of_service, str)

        if supported_nips is not None:
            if not isinstance(supported_nips, list):
                raise TypeError(
                    f"supported_nips must be a list or None, not {type(supported_nips)}")
            for nip in supported_nips:
                if not isinstance(nip, (int, str)):
                    raise TypeError(
                        f"supported_nips items must be int or str, not {type(nip)}")

        if limitation is not None:
            if not isinstance(limitation, dict):
                raise TypeError(
                    f"limitation must be a dict or None, not {type(limitation)}")
            self._validate_json_serializable("limitation", limitation)

        if extra_fields is not None:
            if not isinstance(extra_fields, dict):
                raise TypeError(
                    f"extra_fields must be a dict or None, not {type(extra_fields)}")
            self._validate_json_serializable("extra_fields", extra_fields)

        # Assign attributes
        self.relay = relay
        self.generated_at = generated_at
        self.connection_success = connection_success
        self.nip11_success = nip11_success
        self.openable = openable
        self.readable = readable
        self.writable = writable
        self.rtt_open = rtt_open
        self.rtt_read = rtt_read
        self.rtt_write = rtt_write
        self.name = name
        self.description = description
        self.banner = banner
        self.icon = icon
        self.pubkey = pubkey
        self.contact = contact
        self.supported_nips = supported_nips
        self.software = software
        self.version = version
        self.privacy_policy = privacy_policy
        self.terms_of_service = terms_of_service
        self.limitation = limitation
        self.extra_fields = extra_fields

    def _validate_optional_field(self, name: str, value: Any, expected_type: type) -> None:
        """Validate an optional field."""
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(
                f"{name} must be {expected_type.__name__} or None, not {type(value)}")

    def _validate_json_serializable(self, name: str, value: Dict[str, Any]) -> None:
        """Validate that a dictionary is JSON serializable."""
        for key, val in value.items():
            if not isinstance(key, str):
                raise TypeError(
                    f"{name} keys must be strings, not {type(key)}")
            try:
                json.dumps(val)
            except (TypeError, ValueError):
                raise TypeError(f"{name} values must be JSON serializable")

    def __repr__(self) -> str:
        """Return string representation of RelayMetadata."""
        return (f"RelayMetadata(relay={self.relay.url}, "
                f"connection_success={self.connection_success}, "
                f"readable={self.readable}, writable={self.writable})")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert RelayMetadata to dictionary.

        Returns:
            Dictionary representation of the metadata
        """
        return {
            "relay": self.relay.to_dict(),
            "generated_at": self.generated_at,
            "connection_success": self.connection_success,
            "nip11_success": self.nip11_success,
            "openable": self.openable,
            "readable": self.readable,
            "writable": self.writable,
            "rtt_open": self.rtt_open,
            "rtt_read": self.rtt_read,
            "rtt_write": self.rtt_write,
            "name": self.name,
            "description": self.description,
            "banner": self.banner,
            "icon": self.icon,
            "pubkey": self.pubkey,
            "contact": self.contact,
            "supported_nips": self.supported_nips,
            "software": self.software,
            "version": self.version,
            "privacy_policy": self.privacy_policy,
            "terms_of_service": self.terms_of_service,
            "limitation": self.limitation,
            "extra_fields": self.extra_fields,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelayMetadata":
        """
        Create RelayMetadata from dictionary.

        Args:
            data: Dictionary containing metadata

        Returns:
            RelayMetadata object
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, not {type(data)}")

        if "relay" not in data:
            raise KeyError("data must contain 'relay' key")
        if "generated_at" not in data:
            raise KeyError("data must contain 'generated_at' key")

        relay = Relay.from_dict(data["relay"])

        return cls(
            relay=relay,
            generated_at=data["generated_at"],
            connection_success=data.get("connection_success", False),
            nip11_success=data.get("nip11_success", False),
            openable=data.get("openable"),
            readable=data.get("readable"),
            writable=data.get("writable"),
            rtt_open=data.get("rtt_open"),
            rtt_read=data.get("rtt_read"),
            rtt_write=data.get("rtt_write"),
            name=data.get("name"),
            description=data.get("description"),
            banner=data.get("banner"),
            icon=data.get("icon"),
            pubkey=data.get("pubkey"),
            contact=data.get("contact"),
            supported_nips=data.get("supported_nips"),
            software=data.get("software"),
            version=data.get("version"),
            privacy_policy=data.get("privacy_policy"),
            terms_of_service=data.get("terms_of_service"),
            limitation=data.get("limitation"),
            extra_fields=data.get("extra_fields"),
        )

    @property
    def is_healthy(self) -> bool:
        """Check if relay appears to be healthy."""
        return (self.connection_success and
                (self.readable is True or self.writable is True))

    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get relay capabilities summary."""
        return {
            "readable": self.readable or False,
            "writable": self.writable or False,
            "openable": self.openable or False,
        }
