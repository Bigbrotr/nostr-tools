"""Nostr relay representation and validation."""

from typing import Dict, Any
from ..utils import find_websocket_relay_urls


class Relay:
    """
    Class to represent a NOSTR relay.

    Attributes:
        url: str, URL of the relay
        network: str, network type ("clearnet" or "tor")
    """

    def __init__(self, url: str) -> None:
        """
        Initialize a Relay object.

        Args:
            url: WebSocket URL of the relay

        Raises:
            TypeError: If url is not a string
            ValueError: If url is not a valid clearnet or tor websocket URL
        """
        if not isinstance(url, str):
            raise TypeError(f"url must be a str, not {type(url)}")

        urls = find_websocket_relay_urls(url)
        if not urls:
            raise ValueError(
                f"Invalid URL format: {url}. Must be a valid clearnet or tor websocket URL."
            )

        url = urls[0]

        # Determine network type
        if url.removeprefix("wss://").partition(":")[0].endswith(".onion"):
            self.network = "tor"
        else:
            self.network = "clearnet"

        self.url = url

    def __repr__(self) -> str:
        """Return string representation of the Relay."""
        return f"Relay(url={self.url}, network={self.network})"

    def __eq__(self, other) -> bool:
        """Check equality with another Relay."""
        if not isinstance(other, Relay):
            return False
        return (
            self.url == other.url and
            self.network == other.network
        )

    def __ne__(self, other) -> bool:
        """Check inequality with another Relay."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Return hash of the relay."""
        return hash((self.url, self.network))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relay":
        """
        Create a Relay object from a dictionary.

        Args:
            data: Dictionary containing relay data

        Returns:
            Relay object

        Raises:
            RelayConnectionError: If data is invalid
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, not {type(data)}")

        if "url" not in data:
            raise ValueError("data must contain key 'url'")

        return cls(data["url"])

    def to_dict(self) -> Dict[str, Any]:
        """
        Return the Relay object as a dictionary.

        Returns:
            Dictionary representation of the relay
        """
        return {
            "url": self.url,
            "network": self.network
        }
