"""Nostr relay representation and validation."""

from typing import Dict, Any
from ..utils.network import find_websocket_relay_urls
from ..exceptions.errors import RelayConnectionError


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
            RelayConnectionError: If URL is invalid
        """
        if not isinstance(url, str):
            raise RelayConnectionError(f"url must be a str, not {type(url)}")

        urls = find_websocket_relay_urls(url)
        if not urls:
            raise RelayConnectionError(
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
        return self.url == other.url

    def __hash__(self) -> int:
        """Return hash of the relay."""
        return hash(self.url)

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
            raise RelayConnectionError(
                f"data must be a dict, not {type(data)}")

        if "url" not in data:
            raise RelayConnectionError("data must contain key 'url'")

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

    @property
    def domain(self) -> str:
        """Get the domain part of the relay URL."""
        return self.url.removeprefix("wss://").removeprefix("ws://").split("/")[0]

    @property
    def is_tor(self) -> bool:
        """Check if this is a Tor (.onion) relay."""
        return self.network == "tor"

    @property
    def is_clearnet(self) -> bool:
        """Check if this is a clearnet relay."""
        return self.network == "clearnet"
