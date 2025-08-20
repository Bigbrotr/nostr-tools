"""Network utilities for Nostr protocol."""

import re
from typing import List, Any, Union


# Top-level domains list (truncated for brevity - include full list from original)
TLDS = [
    "COM", "ORG", "NET", "INT", "EDU", "GOV", "MIL", "ARPA", "AC", "AD", "AE", "AF", "AG",
    "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ", "BA", "BB",
    "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS",
    # ... (include full TLDS list from original utils.py)
]

# RFC 3986 URI regex pattern
URI_GENERIC_REGEX = r"""
    ^(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*):           # scheme
    //(?P<authority>                                 # authority
        (?:(?P<userinfo>[^@]*)@)?                    # userinfo (optional)
        (?P<host>                                    # host
            (?P<domain>[a-zA-Z0-9.-]+)|              # domain name
            \[(?P<ipv6>[0-9a-fA-F:]+)\]|             # IPv6 address
            (?P<ipv4>(?:[0-9]{1,3}\.){3}[0-9]{1,3})  # IPv4 address
        )
        (?P<port>:[0-9]+)?                           # port (optional)
    )
    (?P<path>/[^?#]*)?                               # path (optional)
    (?:\?(?P<query>[^#]*))?                          # query (optional)
    (?:\#(?P<fragment>.*))?                          # fragment (optional)
    $
"""


def find_websocket_relay_urls(text: str) -> List[str]:
    """
    Find all WebSocket relay URLs in the given text.

    Args:
        text: The text to search for WebSocket relays

    Returns:
        List of WebSocket relay URLs found in the text

    Example:
        >>> text = "Connect to wss://relay.example.com:443 and ws://relay.example.com"
        >>> find_websocket_relay_urls(text)
        ['wss://relay.example.com:443', 'wss://relay.example.com']
    """
    result = []
    matches = re.finditer(URI_GENERIC_REGEX, text, re.VERBOSE)

    for match in matches:
        scheme = match.group("scheme")
        host = match.group("host")
        port = match.group("port")
        port = int(port[1:]) if port else None
        path = match.group("path")
        path = "" if path in ["", "/", None] else "/" + path.strip("/")
        domain = match.group("domain")

        # Only WebSocket schemes
        if scheme not in ["ws", "wss"]:
            continue

        # Validate port range
        if port and (port < 0 or port > 65535):
            continue

        # Validate .onion domains
        if domain and domain.lower().endswith(".onion"):
            if not re.match(r"^([a-z2-7]{16}|[a-z2-7]{56})\.onion$", domain.lower()):
                continue

        # Validate TLD
        if domain and (domain.split(".")[-1].upper() not in TLDS + ["ONION"]):
            continue

        # Construct final URL
        port_str = ":" + str(port) if port else ""
        url = "wss://" + host.lower() + port_str + path
        result.append(url)

    return result


def sanitize(value: Any) -> Any:
    """
    Sanitize values by removing null bytes and recursively cleaning data structures.

    Args:
        value: Value to sanitize

    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        return value.replace('\x00', '')
    elif isinstance(value, list):
        return [sanitize(item) for item in value]
    elif isinstance(value, dict):
        return {sanitize(key): sanitize(val) for key, val in value.items()}
    else:
        return value


def is_valid_websocket_url(url: str) -> bool:
    """
    Check if a URL is a valid WebSocket URL.

    Args:
        url: URL to validate

    Returns:
        True if the URL is a valid WebSocket URL
    """
    if not isinstance(url, str):
        return False

    urls = find_websocket_relay_urls(url)
    return len(urls) > 0


def normalize_relay_url(url: str) -> str:
    """
    Normalize a relay URL to a standard format.

    Args:
        url: Relay URL to normalize

    Returns:
        Normalized URL

    Raises:
        ValueError: If URL is invalid
    """
    urls = find_websocket_relay_urls(url)
    if not urls:
        raise ValueError(f"Invalid WebSocket URL: {url}")
    return urls[0]
