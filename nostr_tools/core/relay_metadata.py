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
        connection_success: bool,
        nip11_success: bool,
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

        Raises:
            TypeError: If any argument is of incorrect type
            ValueError: If any argument has an invalid value
        """
        # Validate inputs
        to_validate = [
            ("relay", relay, Relay, True),
            ("generated_at", generated_at, int, True),
            ("connection_success", connection_success, bool, True),
            ("nip11_success", nip11_success, bool, True),
            ("openable", openable, bool, False),
            ("readable", readable, bool, False),
            ("writable", writable, bool, False),
            ("rtt_open", rtt_open, int, False),
            ("rtt_read", rtt_read, int, False),
            ("rtt_write", rtt_write, int, False),
            ("name", name, str, False),
            ("description", description, str, False),
            ("banner", banner, str, False),
            ("icon", icon, str, False),
            ("pubkey", pubkey, str, False),
            ("contact", contact, str, False),
            ("supported_nips", supported_nips, list, False),
            ("software", software, str, False),
            ("version", version, str, False),
            ("privacy_policy", privacy_policy, str, False),
            ("terms_of_service", terms_of_service, str, False),
            ("limitation", limitation, dict, False),
            ("extra_fields", extra_fields, dict, False),
        ]
        for field_name, field_value, expected_type, is_required in to_validate:
            if is_required and field_value is None:
                raise ValueError(
                    f"{field_name} is required and cannot be None")
            if field_value is not None and not isinstance(field_value, expected_type):
                raise TypeError(
                    f"{field_name} must be of type {expected_type.__name__} or None, not {type(field_value)}"
                )
        if generated_at < 0:
            raise ValueError("generated_at must be a non-negative integer")
        if supported_nips is not None:
            for nip in supported_nips:
                if not isinstance(nip, (int, str)):
                    raise TypeError(
                        f"supported_nips items must be int or str, not {type(nip)}"
                    )
        to_validate = [
            ("limitation", limitation),
            ("extra_fields", extra_fields),
        ]
        for field_name, field_value in to_validate:
            for key, val in field_value.items():
                if not isinstance(key, str):
                    raise TypeError(
                        f"{field_name} keys must be strings, not {type(key)}"
                    )
                try:
                    json.dumps(val)
                except (TypeError, ValueError):
                    raise TypeError(
                        f"{field_name} values must be JSON serializable")

        # Assign attributes
        self.relay = relay
        self.generated_at = generated_at
        self.connection_success = connection_success
        self.nip11_success = nip11_success
        self.openable = openable if connection_success else None
        self.readable = readable if connection_success else None
        self.writable = writable if connection_success else None
        self.rtt_open = rtt_open if connection_success else None
        self.rtt_read = rtt_read if connection_success else None
        self.rtt_write = rtt_write if connection_success else None
        self.name = name if nip11_success else None
        self.description = description if nip11_success else None
        self.banner = banner if nip11_success else None
        self.icon = icon if nip11_success else None
        self.pubkey = pubkey if nip11_success else None
        self.contact = contact if nip11_success else None
        self.supported_nips = supported_nips if nip11_success else None
        self.software = software if nip11_success else None
        self.version = version if nip11_success else None
        self.privacy_policy = privacy_policy if nip11_success else None
        self.terms_of_service = terms_of_service if nip11_success else None
        self.limitation = limitation if connection_success else None
        self.extra_fields = extra_fields if connection_success else None

    def __repr__(self) -> str:
        """Return string representation of RelayMetadata."""
        return (
            f"RelayMetadata(relay={self.relay}, generated_at={self.generated_at}, "
            f"connection_success={self.connection_success}, nip11_success={self.nip11_success}, "
            f"openable={self.openable}, readable={self.readable}, writable={self.writable}, "
            f"rtt_open={self.rtt_open}, rtt_read={self.rtt_read}, rtt_write={self.rtt_write}, "
            f"name={self.name}, description={self.description}, banner={self.banner}, icon={self.icon}, "
            f"pubkey={self.pubkey}, contact={self.contact}, supported_nips={self.supported_nips}, "
            f"software={self.software}, version={self.version}, privacy_policy={self.privacy_policy}, "
            f"terms_of_service={self.terms_of_service}, limitation={self.limitation}, "
            f"extra_fields={self.extra_fields})"
        )

    def __eq__(self, other) -> bool:
        """Check equality with another RelayMetadata."""
        if not isinstance(other, RelayMetadata):
            return False
        return (
            self.relay == other.relay and
            self.generated_at == other.generated_at and
            self.connection_success == other.connection_success and
            self.nip11_success == other.nip11_success and
            self.openable == other.openable and
            self.readable == other.readable and
            self.writable == other.writable and
            self.rtt_open == other.rtt_open and
            self.rtt_read == other.rtt_read and
            self.rtt_write == other.rtt_write and
            self.name == other.name and
            self.description == other.description and
            self.banner == other.banner and
            self.icon == other.icon and
            self.pubkey == other.pubkey and
            self.contact == other.contact and
            self.supported_nips == other.supported_nips and
            self.software == other.software and
            self.version == other.version and
            self.privacy_policy == other.privacy_policy and
            self.terms_of_service == other.terms_of_service and
            self.limitation == other.limitation and
            self.extra_fields == other.extra_fields
        )

    def __ne__(self, other) -> bool:
        """Check inequality with another RelayMetadata."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Return hash of the RelayMetadata."""
        return hash((
            self.relay,
            self.generated_at,
            self.connection_success,
            self.nip11_success,
            self.openable,
            self.readable,
            self.writable,
            self.rtt_open,
            self.rtt_read,
            self.rtt_write,
            self.name,
            self.description,
            self.banner,
            self.icon,
            self.pubkey,
            self.contact,
            tuple(self.supported_nips) if self.supported_nips else None,
            self.software,
            self.version,
            self.privacy_policy,
            self.terms_of_service,
            frozenset(self.limitation.items()) if self.limitation else None,
            frozenset(self.extra_fields.items()
                      ) if self.extra_fields else None,
        ))

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
        required_keys = ["relay", "generated_at",
                         "connection_success", "nip11_success"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"data must contain key {key}")
        return cls(
            relay=data["relay"],
            generated_at=data["generated_at"],
            connection_success=data["connection_success"],
            nip11_success=data["nip11_success"],
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert RelayMetadata to dictionary.

        Returns:
            Dictionary representation of the metadata
        """
        return {
            "relay": self.relay,
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
