"""
Nostr relay representation and validation.

This module provides the Relay class for representing and validating
Nostr relay configurations, including URL validation and network type
detection.
"""

from typing import Any

from ..utils import find_websocket_relay_urls


class Relay:
    """
    Class to represent a NOSTR relay.

    This class handles validation and representation of Nostr relay
    configurations, automatically detecting network type (clearnet or tor)
    based on the URL format.

    Attributes:
        url (str): WebSocket URL of the relay
        network (str): Network type ("clearnet" or "tor")
    """

    def __init__(self, url: str) -> None:
        """
        Initialize a Relay object with URL validation.

        Args:
            url (str): WebSocket URL of the relay (ws:// or wss://)

        Raises:
            TypeError: If url is not a string
            ValueError: If url is not a valid clearnet or tor websocket URL
        """
        if not isinstance(url, str):
            raise TypeError(f"url must be a str, not {type(url)}")

        # Validate URL format using utility function
        urls = find_websocket_relay_urls(url)
        if not urls:
            raise ValueError(
                f"Invalid URL format: {url}. Must be a valid clearnet or tor websocket URL."
            )

        url = urls[0]

        # Determine network type based on domain
        if url.removeprefix("wss://").partition(":")[0].endswith(".onion"):
            self.network = "tor"
        else:
            self.network = "clearnet"

        self.url = url

    def __repr__(self) -> str:
        """
        Return string representation of the Relay.

        Returns:
            str: String representation showing URL and network type
        """
        return f"Relay(url={self.url}, network={self.network})"

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Relay.

        Args:
            other: Object to compare with

        Returns:
            bool: True if relays are equal, False otherwise
        """
        if not isinstance(other, Relay):
            return False
        return self.url == other.url and self.network == other.network

    def __ne__(self, other: object) -> bool:
        """
        Check inequality with another Relay.

        Args:
            other: Object to compare with

        Returns:
            bool: True if relays are not equal, False otherwise
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        Return hash of the relay.

        Returns:
            int: Hash value for the relay
        """
        return hash((self.url, self.network))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relay":
        """
        Create a Relay object from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing relay data with 'url' key

        Returns:
            Relay: Validated Relay object

        Raises:
            TypeError: If data is not a dictionary
            ValueError: If 'url' key is missing or invalid
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, not {type(data)}")

        if "url" not in data:
            raise ValueError("data must contain key 'url'")

        return cls(data["url"])

    def to_dict(self) -> dict[str, Any]:
        """
        Return the Relay object as a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the relay
        """
        return {"url": self.url, "network": self.network}
