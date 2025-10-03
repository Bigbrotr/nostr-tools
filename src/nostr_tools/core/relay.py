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
    Nostr relay representation following protocol specifications.

    This class handles validation and representation of Nostr relay
    configurations, automatically detecting network type (clearnet or tor)
    based on the URL format.

    Attributes:
        url: WebSocket URL of the relay
        network: Network type ("clearnet" or "tor")
        relay_dict: Internal dictionary representation of the relay
    """

    url: str
    network: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        """Validate and build relay dictionary after initialization."""
        if isinstance(self.url, str):
            urls = find_ws_urls(self.url)
            self.url = urls[0] if urls else self.url
        if self.network is None and isinstance(self.url, str):
            self.network = self.__network
        self.validate()

    def validate(self) -> None:
        """
        Validate the Relay instance.

        Raises:
            TypeError: If any attribute is of incorrect type
            RelayValidationError: If any attribute has an invalid value
        """
        type_checks = [
            ("url", self.url, str),
            ("network", self.network, str),
        ]
        for field_name, field_value, expected_type in type_checks:
            if not isinstance(field_value, expected_type):
                raise TypeError(f"{field_name} must be {expected_type}, got {type(field_value)}")

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
        Check if the Relay is valid.

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.validate()
            return True
        except (TypeError, RelayValidationError):
            return False

    @property
    def __network(self) -> str:
        if not isinstance(self.url, str):
            raise TypeError(f"url must be str, got {type(self.url)}")
        if self.url.removeprefix("wss://").partition(":")[0].endswith(".onion"):
            return "tor"
        else:
            return "clearnet"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relay":
        """
        Create Relay from dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing relay data with 'url' key

        Returns:
            Relay: An instance of Relay

        Raises:
            TypeError: If data is not a dictionary
            ValueError: If 'url' key is missing
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data)}")

        return cls(url=data["url"], network=data.get("network"))

    def to_dict(self) -> dict[str, Any]:
        """
        Convert Relay to dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of Relay
        """
        return {"url": self.url, "network": self.network}
