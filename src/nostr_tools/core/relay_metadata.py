"""
Nostr relay metadata representation with separated NIP data.
"""

import json
from dataclasses import dataclass
from typing import Any
from typing import Optional
from typing import Union

from ..exceptions import Nip11ValidationError
from ..exceptions import Nip66ValidationError
from ..exceptions import RelayMetadataValidationError
from .relay import Relay


@dataclass
class RelayMetadata:
    """
    Comprehensive metadata for a Nostr relay.

    This class stores complete metadata about a relay, combining information
    from multiple Nostr Improvement Proposals (NIPs). It includes:
    - Relay connection and configuration (Relay object)
    - NIP-11: Relay information document (name, description, capabilities)
    - NIP-66: Connection performance metrics (RTT, read/write capabilities)
    - Generation timestamp for tracking when metadata was collected

    The metadata provides a comprehensive view of relay capabilities and
    performance, useful for relay selection, monitoring, and health checks.

    Examples:
        Fetch complete relay metadata:

        >>> relay = Relay("wss://relay.damus.io")
        >>> client = Client(relay)
        >>> metadata = await fetch_relay_metadata(client, private_key, public_key)
        >>> print(f"Relay: {metadata.relay.url}")
        >>> print(f"Name: {metadata.nip11.name if metadata.nip11 else 'Unknown'}")
        >>> print(f"Readable: {metadata.nip66.readable if metadata.nip66 else False}")

        Access NIP-11 information:

        >>> if metadata.nip11:
        ...     print(f"Software: {metadata.nip11.software}")
        ...     print(f"Supported NIPs: {metadata.nip11.supported_nips}")

        Check connection metrics:

        >>> if metadata.nip66:
        ...     print(f"Connection time: {metadata.nip66.rtt_open}ms")
        ...     print(f"Read capable: {metadata.nip66.readable}")
        ...     print(f"Write capable: {metadata.nip66.writable}")

    Raises:
        RelayMetadataValidationError: If metadata validation fails during
            initialization or when invalid data is provided.
    """

    #: The relay object this metadata describes
    relay: Relay
    #: Timestamp when the metadata was generated
    generated_at: int
    #: NIP-11 relay information document data
    nip11: Optional["RelayMetadata.Nip11"] = None
    #: NIP-66 connection and performance data
    nip66: Optional["RelayMetadata.Nip66"] = None

    def __post_init__(self) -> None:
        """
        Validate RelayMetadata after initialization.

        This method is automatically called after the dataclass is created.
        It performs validation to ensure all metadata is properly formatted.

        Raises:
            RelayMetadataValidationError: If metadata validation fails
        """
        self.validate()

    def validate(self) -> None:
        """
        Validate the RelayMetadata instance.

        Raises:
            RelayMetadataValidationError: If relay metadata is invalid
        """
        # Type validation - use class name comparison for compatibility with lazy loading
        if not (isinstance(self.relay, Relay) or type(self.relay).__name__ == "Relay"):
            raise RelayMetadataValidationError(f"relay must be Relay, got {type(self.relay)}")
        if not isinstance(self.generated_at, int):
            raise RelayMetadataValidationError(
                f"generated_at must be int, got {type(self.generated_at)}"
            )
        if self.nip11 is not None and not (
            isinstance(self.nip11, RelayMetadata.Nip11) or type(self.nip11).__name__ == "Nip11"
        ):
            raise RelayMetadataValidationError(
                f"nip11 must be Nip11 or None, got {type(self.nip11)}"
            )
        if self.nip66 is not None and not (
            isinstance(self.nip66, RelayMetadata.Nip66) or type(self.nip66).__name__ == "Nip66"
        ):
            raise RelayMetadataValidationError(
                f"nip66 must be Nip66 or None, got {type(self.nip66)}"
            )

        if not self.relay.is_valid:
            raise RelayMetadataValidationError(f"relay is invalid: {self.relay}")

        if self.generated_at < 0:
            raise RelayMetadataValidationError("generated_at must be non-negative")

        if self.nip11 is not None and not self.nip11.is_valid:
            raise RelayMetadataValidationError(f"nip11 is invalid: {self.nip11}")

        if self.nip66 is not None and not self.nip66.is_valid:
            raise RelayMetadataValidationError(f"nip66 is invalid: {self.nip66}")

    @property
    def is_valid(self) -> bool:
        """
        Check if all metadata is valid without raising exceptions.

        This property attempts validation and returns True if successful,
        False otherwise. Unlike validate(), this method does not raise
        exceptions, making it safe for conditional checks.

        Returns:
            bool: True if all metadata passes validation checks,
                False if validation fails for any reason.

        Examples:
            >>> metadata = await fetch_relay_metadata(client, sec, pub)
            >>> if metadata.is_valid:
            ...     print("Metadata is valid")
            ...     store_metadata(metadata)
            ... else:
            ...     print("Invalid metadata")

            >>> # Validate before processing
            >>> if not metadata.is_valid:
            ...     logger.warning(f"Invalid metadata for {metadata.relay.url}")
        """
        try:
            self.validate()
            return True
        except RelayMetadataValidationError:
            return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelayMetadata":
        """
        Create RelayMetadata from dictionary representation.

        This method reconstructs a RelayMetadata instance from a dictionary,
        typically used for deserialization from storage or network transmission.

        Args:
            data (dict[str, Any]): Dictionary containing relay metadata with keys:
                - relay (dict): Relay configuration dictionary
                - generated_at (int): Unix timestamp when metadata was generated
                - nip11 (Optional[dict]): NIP-11 relay information or None
                - nip66 (Optional[dict]): NIP-66 connection metrics or None

        Returns:
            RelayMetadata: An instance of RelayMetadata created from the dictionary.

        Raises:
            TypeError: If data is not a dictionary.
            RelayMetadataValidationError: If relay metadata validation fails.

        Examples:
            Load from JSON:

            >>> import json
            >>> with open('relay_metadata.json') as f:
            ...     data = json.load(f)
            >>> metadata = RelayMetadata.from_dict(data)

            Deserialize from database:

            >>> metadata_dict = db.relay_metadata.find_one({"relay.url": url})
            >>> metadata = RelayMetadata.from_dict(metadata_dict)

            Parse API response:

            >>> response = requests.get(f"{api_url}/relay/metadata")
            >>> metadata = RelayMetadata.from_dict(response.json())
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
        Convert RelayMetadata to dictionary representation.

        This method serializes the RelayMetadata instance into a dictionary
        format suitable for JSON encoding, storage, or network transmission.

        Returns:
            dict[str, Any]: Dictionary representation of RelayMetadata with keys:
                - relay (dict): Relay configuration dictionary
                - generated_at (int): Unix timestamp when metadata was generated
                - nip11 (Optional[dict]): NIP-11 relay information or None
                - nip66 (Optional[dict]): NIP-66 connection metrics or None

        Examples:
            Serialize to JSON:

            >>> metadata = await fetch_relay_metadata(client, sec, pub)
            >>> metadata_dict = metadata.to_dict()
            >>> import json
            >>> json_str = json.dumps(metadata_dict, indent=2)
            >>> with open('relay_metadata.json', 'w') as f:
            ...     f.write(json_str)

            Store in database:

            >>> metadata_dict = metadata.to_dict()
            >>> db.relay_metadata.insert_one(metadata_dict)

            Send via API:

            >>> response = requests.post(
            ...     f"{api_url}/relay/metadata",
            ...     json=metadata.to_dict()
            ... )
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
        """

        #: Relay name
        name: Optional[str] = None
        #: Relay description
        description: Optional[str] = None
        #: URL to banner image
        banner: Optional[str] = None
        #: URL to icon image
        icon: Optional[str] = None
        #: Relay public key
        pubkey: Optional[str] = None
        #: Contact information
        contact: Optional[str] = None
        #: List of supported NIPs
        supported_nips: Optional[list[Union[int, str]]] = None
        #: Software name
        software: Optional[str] = None
        #: Software version
        version: Optional[str] = None
        #: URL to privacy policy
        privacy_policy: Optional[str] = None
        #: URL to terms of service
        terms_of_service: Optional[str] = None
        #: Limitation information
        limitation: Optional[dict[str, Any]] = None
        #: Additional fields
        extra_fields: Optional[dict[str, Any]] = None

        def __post_init__(self) -> None:
            """
            Normalize and validate data after initialization.

            This method is automatically called after the dataclass is created.
            It normalizes empty collections to None and validates the NIP-11 data.

            Raises:
                Nip11ValidationError: If NIP-11 data validation fails
            """
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
                Nip11ValidationError: If NIP-11 data is invalid
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
                    raise Nip11ValidationError(
                        f"{field_name} must be {expected_type} or None, got {type(field_value)}"
                    )

            if self.supported_nips is not None:
                if len(self.supported_nips) == 0:
                    raise Nip11ValidationError("supported_nips must not be an empty list")
                if not any(isinstance(nip, (int, str)) for nip in self.supported_nips or []):
                    raise Nip11ValidationError("supported_nips must be a list of int or str")

            checks = [
                ("limitation", self.limitation),
                ("extra_fields", self.extra_fields),
            ]
            for field_name, field_value in checks:
                if field_value is not None:
                    if len(field_value) == 0:
                        raise Nip11ValidationError(f"{field_name} must not be an empty dict")
                    if not all(isinstance(key, str) for key in field_value.keys()):
                        raise Nip11ValidationError(f"All keys in {field_name} must be strings")
                    try:
                        json.dumps(field_value)
                    except (TypeError, ValueError) as e:
                        raise Nip11ValidationError(
                            f"{field_name} must be JSON serializable: {e}"
                        ) from e

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
            except Nip11ValidationError:
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
                Nip11ValidationError: If NIP-11 data is invalid
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
        """

        #: Whether the relay is openable
        openable: bool = False
        #: Whether the relay is readable
        readable: bool = False
        #: Whether the relay is writable
        writable: bool = False
        #: Round-trip time to open connection in ms
        rtt_open: Optional[int] = None
        #: Round-trip time to read data in ms
        rtt_read: Optional[int] = None
        #: Round-trip time to write data in ms
        rtt_write: Optional[int] = None

        def __post_init__(self) -> None:
            """
            Validate data after initialization.

            This method is automatically called after the dataclass is created.
            It validates the NIP-66 connection and performance data.

            Raises:
                Nip66ValidationError: If NIP-66 data validation fails
            """
            self.validate()

        def validate(self) -> None:
            """
            Validate NIP-66 data.

            Raises:
                Nip66ValidationError: If NIP-66 data is invalid
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
                    raise Nip66ValidationError(
                        f"{field_name} must be {expected_type}, got {type(field_value)}"
                    )

            if (self.readable or self.writable) and not self.openable:
                raise Nip66ValidationError("If readable or writable is True, openable must be True")

            checks = [
                ("openable", "rtt_open", self.openable, self.rtt_open),
                ("readable", "rtt_read", self.readable, self.rtt_read),
                ("writable", "rtt_write", self.writable, self.rtt_write),
            ]

            for flag_name, rtt_name, flag_value, rtt_value in checks:
                if flag_value and rtt_value is None:
                    raise Nip66ValidationError(
                        f"{rtt_name} must be provided when {flag_name} is True"
                    )
                if not flag_value and rtt_value is not None:
                    raise Nip66ValidationError(f"{rtt_name} must be None when {flag_name} is False")
                if flag_value and rtt_value is not None and rtt_value < 0:
                    raise Nip66ValidationError(
                        f"{rtt_name} must be non-negative when {flag_name} is True"
                    )

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
            except Nip66ValidationError:
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
                Nip66ValidationError: If NIP-66 data is invalid
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
