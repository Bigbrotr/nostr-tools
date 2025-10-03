"""
Nostr relay metadata representation with separated NIP data.
"""

import json
from dataclasses import dataclass
from typing import Any
from typing import Optional
from typing import Union

from .relay import Relay


@dataclass
class RelayMetadata:
    """
    Comprehensive metadata for a NOSTR relay.

    This class stores metadata about a relay, including information
    from NIP-11 and NIP-66 standards.

    Attributes:
        relay: The relay object this metadata describes
        nip11: NIP-11 relay information document data
        nip66: NIP-66 connection and performance data
        generated_at: Timestamp when the metadata was generated
    """

    relay: Relay
    generated_at: int
    nip11: Optional["RelayMetadata.Nip11"] = None
    nip66: Optional["RelayMetadata.Nip66"] = None

    def __post_init__(self) -> None:
        """Validate RelayMetadata after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate the RelayMetadata instance.

        Raises:
            TypeError: If any attribute is of incorrect type
            ValueError: If any attribute has an invalid value
        """
        if self.nip11 is not None:
            self.nip11.validate()
        if self.nip66 is not None:
            self.nip66.validate()

        # Type validation - use class name comparison for compatibility with lazy loading
        if not (isinstance(self.relay, Relay) or type(self.relay).__name__ == "Relay"):
            raise TypeError(f"relay must be Relay, got {type(self.relay)}")
        if not isinstance(self.generated_at, int):
            raise TypeError(f"generated_at must be int, got {type(self.generated_at)}")

        if self.generated_at < 0:
            raise ValueError("generated_at must be non-negative")

    @property
    def is_valid(self) -> bool:
        """
        Check if all metadata is valid.

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.validate()
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelayMetadata":
        """
        Create RelayMetadata from dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing relay metadata
        Returns:
            RelayMetadata: An instance of RelayMetadata
        Raises:
            TypeError: If data is not a dictionary
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data)}")

        return cls(
            relay=Relay.from_dict(data["relay"]),
            nip11=cls.Nip11.from_dict(data["nip11"])
            if "nip11" in data and data["nip11"] is not None
            else None,
            nip66=cls.Nip66.from_dict(data["nip66"])
            if "nip66" in data and data["nip66"] is not None
            else None,
            generated_at=data["generated_at"],
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert RelayMetadata to dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of RelayMetadata
        """
        return {
            "relay": self.relay.to_dict(),
            "nip66": self.nip66.to_dict() if self.nip66 else None,
            "nip11": self.nip11.to_dict() if self.nip11 else None,
            "generated_at": self.generated_at,
        }

    @dataclass
    class Nip11:
        """
        NIP-11: Relay Information Document

        This module defines the Nip11 class for handling relay information documents
        as specified in NIP-11. It includes validation, normalization, and conversion
        to/from dictionary representations.

        Attributes:
            name: Relay name
            description: Relay description
            banner: URL to banner image
            icon: URL to icon image
            pubkey: Relay public key
            contact: Contact information
            supported_nips: List of supported NIPs
            software: Software name
            version: Software version
            privacy_policy: URL to privacy policy
            terms_of_service: URL to terms of service
            limitation: Limitation information
            extra_fields: Additional fields
        """

        name: Optional[str] = None
        description: Optional[str] = None
        banner: Optional[str] = None
        icon: Optional[str] = None
        pubkey: Optional[str] = None
        contact: Optional[str] = None
        supported_nips: Optional[list[Union[int, str]]] = None
        software: Optional[str] = None
        version: Optional[str] = None
        privacy_policy: Optional[str] = None
        terms_of_service: Optional[str] = None
        limitation: Optional[dict[str, Any]] = None
        extra_fields: Optional[dict[str, Any]] = None

        def __post_init__(self) -> None:
            """Normalize and validate data after initialization."""
            # Normalize empty collections to None
            if self.supported_nips is not None and self.supported_nips == []:
                self.supported_nips = None
            if self.limitation is not None and self.limitation == {}:
                self.limitation = None
            if self.extra_fields is not None and self.extra_fields == {}:
                self.extra_fields = None
            # Validate the data
            self.validate()

        def validate(self) -> None:
            """
            Validate NIP-11 data.

            Raises:
                TypeError: If any attribute is of incorrect type
                ValueError: If any attribute has an invalid value
            """
            # Type validation for string fields
            type_checks: list[tuple[str, Any, Union[type[str], tuple[type, ...]]]] = [
                ("name", self.name, str),
                ("description", self.description, str),
                ("banner", self.banner, str),
                ("icon", self.icon, str),
                ("pubkey", self.pubkey, str),
                ("contact", self.contact, str),
                ("supported_nips", self.supported_nips, (list, type(None))),
                ("software", self.software, str),
                ("version", self.version, str),
                ("privacy_policy", self.privacy_policy, str),
                ("terms_of_service", self.terms_of_service, str),
                ("limitation", self.limitation, (dict, type(None))),
                ("extra_fields", self.extra_fields, (dict, type(None))),
            ]
            for field_name, field_value, expected_type in type_checks:
                if field_value is not None and not isinstance(field_value, expected_type):
                    raise TypeError(
                        f"{field_name} must be {expected_type} or None, got {type(field_value)}"
                    )

            if self.supported_nips is not None:
                if len(self.supported_nips) == 0:
                    raise ValueError("supported_nips must not be an empty list")
                if not any(isinstance(nip, (int, str)) for nip in self.supported_nips or []):
                    raise TypeError("supported_nips must be a list of int or str")

            checks = [
                ("limitation", self.limitation),
                ("extra_fields", self.extra_fields),
            ]
            for field_name, field_value in checks:
                if field_value is not None:
                    if len(field_value) == 0:
                        raise ValueError(f"{field_name} must not be an empty dict")
                    if not all(isinstance(key, str) for key in field_value.keys()):
                        raise TypeError(f"All keys in {field_name} must be strings")
                    try:
                        json.dumps(field_value)
                    except (TypeError, ValueError) as e:
                        raise ValueError(f"{field_name} must be JSON serializable: {e}") from e

        @property
        def is_valid(self) -> bool:
            """
            Check if the NIP-11 data is valid.

            Returns:
                bool: True if valid, False otherwise
            """
            try:
                self.validate()
                return True
            except (TypeError, ValueError):
                return False

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "RelayMetadata.Nip11":
            """
            Create Nip11 from dictionary.

            Args:
                data (dict[str, Any]): Dictionary containing NIP-11 data
            Returns:
                RelayMetadata.Nip11: An instance of Nip11
            Raises:
                TypeError: If data is not a dictionary
            """
            if not isinstance(data, dict):
                raise TypeError(f"data must be a dict, got {type(data)}")

            return cls(
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

        def to_dict(self) -> dict[str, Any]:
            """
            Convert Nip11 to dictionary.

            Returns:
                dict[str, Any]: Dictionary representation of Nip11
            """
            return {
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

    @dataclass
    class Nip66:
        """
        NIP-66: Relay Connection and Performance Data

        This module defines the Nip66 class for handling relay connection and performance
        data as specified in NIP-66. It includes validation, conversion to/from dictionary
        representations, and a property to check data validity.

        Attributes:
            openable: Whether the relay is openable
            readable: Whether the relay is readable
            writable: Whether the relay is writable
            rtt_open: Round-trip time to open connection in ms
            rtt_read: Round-trip time to read data in ms
            rtt_write: Round-trip time to write data in ms
        """

        openable: bool = False
        readable: bool = False
        writable: bool = False
        rtt_open: Optional[int] = None
        rtt_read: Optional[int] = None
        rtt_write: Optional[int] = None

        def __post_init__(self) -> None:
            """Validate data after initialization."""
            self.validate()

        def validate(self) -> None:
            """
            Validate NIP-66 data.

            Raises:
                TypeError: If any attribute is of incorrect type
                ValueError: If any attribute has an invalid value
            """
            type_checks: list[tuple[str, Any, Union[type[bool], tuple[type, ...]]]] = [
                ("openable", self.openable, bool),
                ("readable", self.readable, bool),
                ("writable", self.writable, bool),
                ("rtt_open", self.rtt_open, (int, type(None))),
                ("rtt_read", self.rtt_read, (int, type(None))),
                ("rtt_write", self.rtt_write, (int, type(None))),
            ]

            for field_name, field_value, expected_type in type_checks:
                if not isinstance(field_value, expected_type):
                    raise TypeError(
                        f"{field_name} must be {expected_type}, got {type(field_value)}"
                    )

            if (self.readable or self.writable) and not self.openable:
                raise ValueError("If readable or writable is True, openable must be True")

            checks = [
                ("openable", "rtt_open", self.openable, self.rtt_open),
                ("readable", "rtt_read", self.readable, self.rtt_read),
                ("writable", "rtt_write", self.writable, self.rtt_write),
            ]

            for flag_name, rtt_name, flag_value, rtt_value in checks:
                if flag_value and rtt_value is None:
                    raise ValueError(f"{rtt_name} must be provided when {flag_name} is True")
                if not flag_value and rtt_value is not None:
                    raise ValueError(f"{rtt_name} must be None when {flag_name} is False")
                if flag_value and rtt_value is not None and rtt_value < 0:
                    raise ValueError(f"{rtt_name} must be non-negative when {flag_name} is True")

        @property
        def is_valid(self) -> bool:
            """
            Check if the NIP-66 data is valid.

            Returns:
                bool: True if valid, False otherwise
            """
            try:
                self.validate()
                return True
            except (TypeError, ValueError):
                return False

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "RelayMetadata.Nip66":
            """
            Create Nip66 from dictionary.

            Args:
                data (dict[str, Any]): Dictionary containing NIP-66 data
            Returns:
                RelayMetadata.Nip66: An instance of Nip66
            Raises:
                TypeError: If data is not a dictionary
            """
            if not isinstance(data, dict):
                raise TypeError(f"data must be a dict, got {type(data)}")

            return cls(
                openable=data.get("openable", False),
                readable=data.get("readable", False),
                writable=data.get("writable", False),
                rtt_open=data.get("rtt_open"),
                rtt_read=data.get("rtt_read"),
                rtt_write=data.get("rtt_write"),
            )

        def to_dict(self) -> dict[str, Any]:
            """
            Convert Nip66 to dictionary.

            Returns:
                dict[str, Any]: Dictionary representation of Nip66
            """
            return {
                "openable": self.openable,
                "readable": self.readable,
                "writable": self.writable,
                "rtt_open": self.rtt_open,
                "rtt_read": self.rtt_read,
                "rtt_write": self.rtt_write,
            }
