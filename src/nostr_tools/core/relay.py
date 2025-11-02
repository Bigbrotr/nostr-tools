"""
Nostr relay representation and validation.

This module provides the Relay class for representing and validating
Nostr relay configurations, including URL validation and network type
detection.
"""

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Optional

from ..exceptions import RelayValidationError
from ..utils import find_ws_urls


@dataclass
class Relay:
    """
    Nostr relay configuration and representation.

    This class handles validation and representation of Nostr relay
    configurations. It automatically detects and validates network type
    (clearnet or Tor) based on the WebSocket URL format. The URL is
    validated and normalized upon initialization.

    Examples:
        Create a clearnet relay:

        >>> relay = Relay("wss://relay.damus.io")
        >>> print(relay.network)
        clearnet

        Create a Tor relay:

        >>> tor_relay = Relay("wss://relay.onion")
        >>> print(tor_relay.network)
        tor

        URL is normalized automatically:

        >>> relay = Relay("relay.damus.io")  # Missing wss://
        >>> print(relay.url)
        wss://relay.damus.io

        Create from dictionary:

        >>> relay_data = {"url": "wss://relay.damus.io"}
        >>> relay = Relay.from_dict(relay_data)

        Validate a relay:

        >>> try:
        ...     relay.validate()
        ...     print("Relay is valid")
        ... except RelayValidationError as e:
        ...     print(f"Validation failed: {e}")

    Raises:
        RelayValidationError: If URL is not a valid WebSocket URL or
            network type doesn't match the URL.
    """

    #: WebSocket URL of the relay (wss:// or ws://). Must be a valid WebSocket URL. Automatically normalized. Examples: "wss://relay.damus.io", "wss://nostr.wine"
    url: str
    #: Network type, automatically detected from URL. "clearnet" for standard internet relays, "tor" for .onion Tor hidden service relays.
    network: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        """
        Validate and normalize the Relay instance after initialization.

        This method is automatically called after the dataclass is created.
        It normalizes the URL, auto-detects the network type if not provided,
        and validates the relay configuration.

        Raises:
            RelayValidationError: If URL or network configuration is invalid.
        """
        if isinstance(self.url, str):
            urls = find_ws_urls(self.url)
            self.url = urls[0] if urls else self.url
        if self.network is None and isinstance(self.url, str):
            self.network = self.__network
        self.validate()

    def validate(self) -> None:
        """
        Validate the Relay instance against protocol requirements.

        Performs comprehensive validation including:
        - Type checking for url and network attributes
        - WebSocket URL format validation (must be ws:// or wss://)
        - Network type consistency with URL (.onion for Tor)
        - URL normalization and format compliance

        Raises:
            RelayValidationError: If url is not a valid WebSocket URL,
                or network type doesn't match the URL pattern.

        Examples:
            >>> relay = Relay("wss://relay.damus.io")
            >>> relay.validate()  # Passes validation

            >>> invalid_relay = Relay("https://not-a-websocket.com")
            >>> invalid_relay.validate()  # Raises RelayValidationError
        """
        type_checks = [
            ("url", self.url, str),
            ("network", self.network, str),
        ]
        for field_name, field_value, expected_type in type_checks:
            if not isinstance(field_value, expected_type):
                raise RelayValidationError(
                    f"{field_name} must be {expected_type}, got {type(field_value)}"
                )

        urls = find_ws_urls(self.url)
        if len(urls) != 1 or urls[0] != self.url:
            raise RelayValidationError(f"url must be a valid WebSocket URL, got {self.url}")

        if self.network != self.__network:
            raise RelayValidationError(
                f"network must be '{self.__network}' based on the url, got {self.network}"
            )

    @property
    def is_valid(self) -> bool:
        """
        Check if the Relay is valid without raising exceptions.

        This property attempts validation and returns True if successful,
        False otherwise. Unlike validate(), this method does not raise
        exceptions, making it safe for conditional checks.

        Returns:
            bool: True if the relay passes all validation checks,
                False if validation fails for any reason.

        Examples:
            >>> relay = Relay("wss://relay.damus.io")
            >>> if relay.is_valid:
            ...     client = Client(relay)
            ... else:
            ...     print("Invalid relay configuration")
        """
        try:
            self.validate()
            return True
        except RelayValidationError:
            return False

    @property
    def __network(self) -> str:
        """
        Determine network type based on URL format.

        Automatically detects whether the relay URL is for clearnet or Tor
        based on the domain format. Tor relays use .onion domains.

        Returns:
            str: Network type - "tor" for .onion domains, "clearnet" for others

        Raises:
            TypeError: If url is not a string
        """
        if not isinstance(self.url, str):
            raise TypeError(f"url must be str, got {type(self.url)}")
        if self.url.removeprefix("wss://").partition(":")[0].endswith(".onion"):
            return "tor"
        else:
            return "clearnet"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relay":
        """
        Create a Relay instance from a dictionary representation.

        This class method constructs a Relay from a dictionary, typically
        used for deserialization from JSON or database records.

        Args:
            data (dict[str, Any]): Dictionary containing relay configuration.
                Required keys:
                - url (str): WebSocket URL of the relay
                Optional keys:
                - network (str): Network type (auto-detected if omitted)

        Returns:
            Relay: A new Relay instance created from the dictionary data.

        Raises:
            TypeError: If data is not a dictionary.
            KeyError: If required 'url' key is missing.
            RelayValidationError: If the resulting relay fails validation.

        Examples:
            Create from configuration:

            >>> config = {"url": "wss://relay.damus.io"}
            >>> relay = Relay.from_dict(config)

            Parse from JSON:

            >>> import json
            >>> json_str = '{"url": "wss://relay.damus.io", "network": "clearnet"}'
            >>> relay_dict = json.loads(json_str)
            >>> relay = Relay.from_dict(relay_dict)

            Load from database:

            >>> relay_data = db.relays.find_one({"name": "damus"})
            >>> relay = Relay.from_dict(relay_data)
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data)}")

        return cls(url=data["url"], network=data.get("network"))

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Relay object to a dictionary representation.

        This method serializes the Relay instance into a dictionary format
        suitable for JSON encoding, storage, or transmission.

        Returns:
            dict[str, Any]: Dictionary containing relay fields with keys:
                - url (str): WebSocket URL of the relay
                - network (str): Network type ("clearnet" or "tor")

        Examples:
            Serialize to JSON:

            >>> relay = Relay("wss://relay.damus.io")
            >>> relay_dict = relay.to_dict()
            >>> import json
            >>> json_str = json.dumps(relay_dict)
            >>> print(json_str)
            {"url": "wss://relay.damus.io", "network": "clearnet"}

            Store in database:

            >>> relay_data = relay.to_dict()
            >>> db.relays.insert_one(relay_data)

            Create client configuration:

            >>> config = {
            ...     "relay": relay.to_dict(),
            ...     "timeout": 10
            ... }
        """
        return {"url": self.url, "network": self.network}
