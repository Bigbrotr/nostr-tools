"""
Utility functions for Nostr protocol operations.

This module provides various utility functions for working with the Nostr
protocol, including URL parsing, cryptographic operations, data sanitization,
and encoding/decoding utilities.

The main categories of utilities include:

WebSocket Relay Discovery:
    - find_websocket_relay_urls: Extract and validate WebSocket URLs from text

Data Sanitization:
    - sanitize: Remove null bytes and clean data structures recursively

Cryptographic Operations:
    - calc_event_id: Calculate Nostr event IDs according to NIP-01
    - verify_sig: Verify Schnorr signatures for events
    - sig_event_id: Create Schnorr signatures for event IDs
    - generate_event: Create complete signed events with optional proof-of-work
    - validate_keypair: Validate private/public key pairs
    - generate_keypair: Generate new secp256k1 key pairs

Encoding Utilities:
    - to_bech32: Convert hex strings to Bech32 format (npub, nsec, etc.)
    - to_hex: Convert Bech32 strings back to hex format

Response Parsing:
    - parse_nip11_response: Parse and validate NIP-11 relay information
    - parse_connection_response: Parse relay connection test results

Constants:
    - TLDS: List of valid top-level domains for URL validation
    - URI_GENERIC_REGEX: Comprehensive URI regex pattern following RFC 3986

All cryptographic functions use the secp256k1 elliptic curve and Schnorr
signatures as specified in the Nostr protocol. URL validation supports
both clearnet and Tor (.onion) domains.

Example:
    Basic usage of key utility functions:

    >>> # Generate a new key pair
    >>> private_key, public_key = generate_keypair()

    >>> # Create a signed event
    >>> event = generate_event(
    ...     private_key, public_key,
    ...     kind=1, tags=[], content="Hello Nostr!"
    ... )

    >>> # Verify the event signature
    >>> is_valid = verify_sig(event['id'], event['pubkey'], event['sig'])

    >>> # Convert keys to Bech32 format
    >>> npub = to_bech32('npub', public_key)
    >>> nsec = to_bech32('nsec', private_key)

    >>> # Find relay URLs in text
    >>> text = "Connect to wss://relay.damus.io"
    >>> relays = find_websocket_relay_urls(text)
"""

import hashlib
import json
import os
import re
import time
from typing import Any, Optional
from urllib import request

import bech32
import secp256k1


# https://data.iana.org/TLD/tlds-alpha-by-domain.txt
def _load_tlds() -> list[str]:
    """
    Load TLD list from IANA registry.

    Returns:
        List[str]: List of valid top-level domains in uppercase

    Raises:
        Exception: If unable to fetch TLD list from IANA
    """
    try:
        with request.urlopen(
            "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
        ) as response:
            content = response.read().decode("utf-8")
        # Skip comment lines and empty lines
        tlds = []
        for line in content.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                tlds.append(line.upper())
        return tlds
    except Exception as e:
        raise Exception(f"Failed to load TLD list from IANA: {e}") from e


# Load TLDs dynamically from IANA
TLDS = _load_tlds()


# https://www.rfc-editor.org/rfc/rfc3986
# URI = scheme ":" hier-part [ "?" query ] [ "#" fragment ]
# scheme      = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
# hier-part   = "//" authority path-abempty
#               / path-absolute
#               / path-rootless / path-empty
# authority   = [ userinfo "@" ] host [ ":" port ]
# userinfo    = *( unreserved / pct-encoded / sub-delims / ":" )
# host        = IP-literal / IPv4address / reg-name
# port        = *DIGIT
# path-abempty = *( "/" segment )

# scheme:    https
# hier-part: //user:pass@www.example.com:443/path/to/resource
# authority: user:pass@www.example.com:443
#     userinfo: user:pass
#     host: www.example.com
#     port: 443
# path: /path/to/resource
# query: query=value
# fragment: fragment
URI_GENERIC_REGEX = r"""
    # ==== Scheme ====
    (?P<scheme>[a-zA-Z][a-zA-Z0-9+\-.]*):       # Group 1 for the scheme:
                                               # - Starts with a letter
                                               # - Followed by letters, digits, '+', '-', or '.'
                                               # - Ends with a colon ':'

    \/\/                                       # Double forward slashes '//' separating scheme and authority

    # ==== Optional User Info ====
    (?P<userinfo>                              # Group 2 for optional userinfo group
        [A-Za-z0-9\-\._~!$&'()*+,;=:%]*@       # Userinfo (username[:password]) part, ending with '@'
                                               # - Includes unreserved, sub-delims, ':' and '%'
    )?                                         # Entire userinfo is optional

    # ==== Host (IPv6, IPv4, or Domain) ====
    (?P<host>                                  # Group 3 for host group
        # --- IPv6 Address ---
        \[                                     # Opening square bracket
            (?P<ipv6>([0-9a-fA-F]{1,4}:){7}     # Group 4 for IPv6 address part
                ([0-9a-fA-F]{1,4}))             # Final 1-4 hex digits (total 8 groups)
        \]                                     # Closing square bracket

        |                                      # OR

        # --- IPv4 Address ---
        (?P<ipv4>(\d{1,3}\.){3}                 # Group 5 for IPv4 address part
            \d{1,3})                            # Final group of 1 to 3 digits (e.g., 192.168.0.1)

        |                                      # OR

        # --- Registered Domain Name ---
        (?P<domain>                             # Group 6 for domain part
            (?:                                 # Non-capturing group for domain labels:
                [a-zA-Z0-9]                     # Label must start with a letter or digit
                (?:[a-zA-Z0-9-]{0,61}           # Label can contain letters, digits, and hyphens
                [a-zA-Z0-9])?                   # Label must end with a letter or digit
                \.                              # Dot separating labels
            )+                                    # Repeat for each subdomain
            [a-zA-Z]{2,}                         # TLD must be at least 2 alphabetic characters
        )                                        # End of domain group

        # |                                       # OR

        # (?P<localhost>localhost)                 # Group 7 Special case for 'localhost'
    )                                          # End of host group

    # ==== Optional Port ====
    (?P<port>:\d+)?                             # Group 8 for optional port number prefixed by a colon (e.g., :80)

    # ==== Path ====
    (?P<path>                                  # Group 9 for the path group
        /?                                      # Optional leading slash
        (?:                                     # Non-capturing group for path segments
            [a-zA-Z0-9\-_~!$&'()*+,;=:%]+       # Path segments (e.g., '/files', '/images', etc.)
            (?:/[a-zA-Z0-9\-_~!$&'()*+,;=:%]+)* # Optional repeated path segments
            (?:\.[a-zA-Z0-9\-]+)*                # Allow a file extension (e.g., '.txt', '.jpg', '.html')
        )?
    )                                          # End of path group

    # ==== Optional Query ====
    (?P<query>\?                                 # Group 10 for query starts with '?'
        [a-zA-Z0-9\-_~!$&'()*+,;=:%/?]*         # Query parameters (key=value pairs or just data)
    )?                                         # Entire query is optional

    # ==== Optional Fragment ====
    (?P<fragment>\#                             # Group 11 for fragment starts with '#'
        [a-zA-Z0-9\-_~!$&'()*+,;=:%/?]*         # Fragment identifier (can include same characters as query)
    )?                                         # Entire fragment is optional
"""


def find_websocket_relay_urls(text: str) -> list[str]:
    """
    Find all WebSocket relay URLs in the given text.

    This function searches for valid WebSocket URLs (ws:// or wss://) in text,
    validates them according to URI standards, and returns normalized URLs.
    It supports both clearnet and Tor (.onion) domains.

    Args:
        text (str): The text to search for WebSocket relays

    Returns:
        List[str]: List of valid WebSocket relay URLs found in the text,
                   normalized to use wss:// scheme

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

        # Only process WebSocket schemes
        if scheme not in ["ws", "wss"]:
            continue

        # Validate port range (0-65535)
        if port and (port < 0 or port > 65535):
            continue

        # Validate .onion domains for Tor relays
        if (
            domain
            and domain.lower().endswith(".onion")
            and not re.match(r"^([a-z2-7]{16}|[a-z2-7]{56})\.onion$", domain.lower())
        ):
            continue

        # Validate TLD for clearnet domains
        if domain and (domain.split(".")[-1].upper() not in [*TLDS, "ONION"]):
            continue

        # Construct final URL (normalize to wss://)
        port_str = ":" + str(port) if port else ""
        url = "wss://" + host.lower() + port_str + path
        result.append(url)

    return result


def sanitize(value: Any) -> Any:
    r"""
    Sanitize values by removing null bytes and recursively cleaning data structures.

    This function removes null bytes (\x00) from strings and recursively processes
    lists and dictionaries to ensure all contained data is sanitized.

    Args:
        value (Any): Value to sanitize (str, list, dict, or other)

    Returns:
        Any: Sanitized value with null bytes removed from strings
    """
    if isinstance(value, str):
        return value.replace("\x00", "")
    elif isinstance(value, list):
        return [sanitize(item) for item in value]
    elif isinstance(value, dict):
        return {sanitize(key): sanitize(val) for key, val in value.items()}
    else:
        return value


def calc_event_id(
    pubkey: str, created_at: int, kind: int, tags: list[list[str]], content: str
) -> str:
    """
    Calculate the event ID for a Nostr event according to NIP-01.

    The event ID is calculated as the SHA-256 hash of the serialized event data
    in the format: [0, pubkey, created_at, kind, tags, content]

    Args:
        pubkey (str): Public key in hex format (64 characters)
        created_at (int): Unix timestamp of event creation
        kind (int): Event kind (0-65535)
        tags (List[List[str]]): List of event tags
        content (str): Event content

    Returns:
        str: Event ID as lowercase hex string (64 characters)
    """
    event_data = [0, pubkey, created_at, kind, tags, content]
    event_json = json.dumps(event_data, separators=(",", ":"), ensure_ascii=False)
    event_bytes = event_json.encode("utf-8")
    event_hash = hashlib.sha256(event_bytes).digest()
    return event_hash.hex()


def verify_sig(event_id: str, pubkey: str, signature: str) -> bool:
    """
    Verify an event signature using Schnorr verification.

    This function verifies that the given signature was created by the private key
    corresponding to the public key for the given event ID.

    Args:
        event_id (str): Event ID in hex format (64 characters)
        pubkey (str): Public key in hex format (64 characters)
        signature (str): Signature in hex format (128 characters)

    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        pub_key = secp256k1.PublicKey(bytes.fromhex("02" + pubkey), True)
        result = pub_key.schnorr_verify(
            bytes.fromhex(event_id), bytes.fromhex(signature), None, raw=True
        )
        return bool(result)
    except (ValueError, TypeError):
        return False


def sig_event_id(event_id: str, private_key: str) -> str:
    """
    Sign an event ID with a private key using Schnorr signatures.

    This function creates a Schnorr signature of the event ID using the
    provided private key.

    Args:
        event_id (str): Event ID in hex format (64 characters)
        private_key (str): Private key in hex format (64 characters)

    Returns:
        str: Signature as hex string (128 characters)
    """
    priv_key = secp256k1.PrivateKey(bytes.fromhex(private_key), raw=True)
    signature = priv_key.schnorr_sign(bytes.fromhex(event_id), bip340tag=None, raw=True)
    return str(signature.hex())


def generate_event(
    private_key: str,
    public_key: str,
    kind: int,
    tags: list[list[str]],
    content: str,
    created_at: Optional[int] = None,
    target_difficulty: Optional[int] = None,
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Generate a signed Nostr event with optional proof-of-work.

    This function creates a complete Nostr event with proper ID calculation,
    signature generation, and optional proof-of-work nonce mining.

    Args:
        private_key (str): Private key in hex format (64 characters)
        public_key (str): Public key in hex format (64 characters)
        kind (int): Event kind (0-65535)
        tags (List[List[str]]): List of event tags
        content (str): Event content
        created_at (Optional[int]): Unix timestamp (defaults to current time)
        target_difficulty (Optional[int]): Proof of work difficulty target (leading zero bits)
        timeout (int): Timeout for proof of work mining in seconds (default: 20)

    Returns:
        Dict[str, Any]: Complete signed event dictionary with keys:
                       id, pubkey, created_at, kind, tags, content, sig
    """

    def count_leading_zero_bits(hex_str: str) -> int:
        """Count leading zero bits in a hex string for proof-of-work."""
        bits = 0
        for char in hex_str:
            val = int(char, 16)
            if val == 0:
                bits += 4
            else:
                bits += 4 - val.bit_length()
                break
        return bits

    original_tags = tags.copy()
    created_at = created_at if created_at is not None else int(time.time())

    if target_difficulty is None:
        # No proof of work required
        tags = original_tags
        event_id = calc_event_id(public_key, created_at, kind, tags, content)
    else:
        # Mine proof of work
        nonce = 0
        non_nonce_tags = [tag for tag in original_tags if tag[0] != "nonce"]
        start_time = time.time()

        while True:
            tags = [*non_nonce_tags, ["nonce", str(nonce), str(target_difficulty)]]
            event_id = calc_event_id(public_key, created_at, kind, tags, content)
            difficulty = count_leading_zero_bits(event_id)

            if difficulty >= target_difficulty:
                break
            if (time.time() - start_time) >= timeout:
                # Timeout reached, use original tags without nonce
                tags = original_tags
                event_id = calc_event_id(public_key, created_at, kind, tags, content)
                break
            nonce += 1

    # Sign the event
    sig = sig_event_id(event_id, private_key)

    return {
        "id": event_id,
        "pubkey": public_key,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": content,
        "sig": sig,
    }


def validate_keypair(private_key: str, public_key: str) -> bool:
    """
    Test if a private/public key pair is valid and matches.

    This function verifies that the given private key generates the
    corresponding public key using secp256k1 elliptic curve cryptography.

    Args:
        private_key (str): Private key in hex format (64 characters)
        public_key (str): Public key in hex format (64 characters)

    Returns:
        bool: True if the key pair is valid and matches, False otherwise
    """
    if len(private_key) != 64 or len(public_key) != 64:
        return False

    try:
        private_key_bytes = bytes.fromhex(private_key)
        private_key_obj = secp256k1.PrivateKey(private_key_bytes)
        generated_public_key = private_key_obj.pubkey.serialize(compressed=True)[
            1:
        ].hex()
        return bool(generated_public_key == public_key)
    except Exception:
        return False


def to_bech32(prefix: str, hex_str: str) -> str:
    """
    Convert a hex string to Bech32 format.

    This function converts hexadecimal data to Bech32 encoding with the
    specified prefix, commonly used for Nostr keys and identifiers.

    Args:
        prefix (str): The prefix for the Bech32 encoding (e.g., 'nsec', 'npub')
        hex_str (str): The hex string to convert

    Returns:
        str: The Bech32 encoded string

    Example:
        >>> to_bech32('npub', '1234567890abcdef...')
        'npub1...'
    """
    byte_data = bytes.fromhex(hex_str)
    data = bech32.convertbits(byte_data, 8, 5, True)
    if data is None:
        return ""
    result = bech32.bech32_encode(prefix, data)
    return str(result) if result is not None else ""


def to_hex(bech32_str: str) -> str:
    """
    Convert a Bech32 string to hex format.

    This function decodes a Bech32 string and returns the underlying
    data as a hexadecimal string.

    Args:
        bech32_str (str): The Bech32 string to convert

    Returns:
        str: The hex encoded string

    Example:
        >>> to_hex('npub1...')
        '1234567890abcdef...'
    """
    _, data = bech32.bech32_decode(bech32_str)
    if data is None:
        return ""
    byte_data = bech32.convertbits(data, 5, 8, False)
    if byte_data is None:
        return ""
    return str(bytes(byte_data).hex())


def generate_keypair() -> tuple[str, str]:
    """
    Generate a new private/public key pair for Nostr.

    This function creates a new secp256k1 key pair suitable for use
    with the Nostr protocol.

    Returns:
        tuple[str, str]: Tuple of (private_key_hex, public_key_hex)
                        Both keys are 64-character hex strings

    Example:
        >>> priv, pub = generate_keypair()
        >>> len(priv), len(pub)
        (64, 64)
    """
    private_key = os.urandom(32)
    private_key_obj = secp256k1.PrivateKey(private_key)
    public_key = private_key_obj.pubkey.serialize(compressed=True)[1:]
    private_key_hex = private_key.hex()
    public_key_hex = public_key.hex()
    return private_key_hex, public_key_hex


def parse_nip11_response(nip11_response):
    """
    Parse NIP-11 relay information document response.

    This function processes the response from a NIP-11 relay information
    endpoint and extracts valid metadata fields with proper validation.

    Args:
        nip11_response: Response data from NIP-11 endpoint (dict expected)

    Returns:
        dict: Parsed NIP-11 metadata with validated fields, or
              {'nip11_success': False} if parsing fails
    """
    if not isinstance(nip11_response, dict):
        return {"nip11_success": False}

    # Extract basic fields from NIP-11 response
    result = {
        "nip11_success": True,
        "name": nip11_response.get("name"),
        "description": nip11_response.get("description"),
        "banner": nip11_response.get("banner"),
        "icon": nip11_response.get("icon"),
        "pubkey": nip11_response.get("pubkey"),
        "contact": nip11_response.get("contact"),
        "supported_nips": nip11_response.get("supported_nips"),
        "software": nip11_response.get("software"),
        "version": nip11_response.get("version"),
        "privacy_policy": nip11_response.get("privacy_policy"),
        "terms_of_service": nip11_response.get("terms_of_service"),
        "limitation": nip11_response.get("limitation"),
        "extra_fields": {
            key: value
            for key, value in nip11_response.items()
            if key
            not in [
                "name",
                "description",
                "banner",
                "icon",
                "pubkey",
                "contact",
                "supported_nips",
                "software",
                "version",
                "privacy_policy",
                "terms_of_service",
                "limitation",
            ]
        },
    }

    # Validate string fields
    string_fields = [
        "name",
        "description",
        "banner",
        "icon",
        "pubkey",
        "contact",
        "software",
        "version",
        "privacy_policy",
        "terms_of_service",
    ]
    for key in string_fields:
        if not (isinstance(result[key], str) or result[key] is None):
            result[key] = None

    # Validate supported_nips list
    if not isinstance(result["supported_nips"], list):
        result["supported_nips"] = None
    else:
        result["supported_nips"] = [
            nip for nip in result["supported_nips"] if isinstance(nip, (int, str))
        ]

    # Validate dictionary fields
    dict_fields = ["limitation", "extra_fields"]
    for key in dict_fields:
        field_value = result[key]
        if not isinstance(field_value, dict):
            result[key] = None
        else:
            data = {}
            for dict_key, value in field_value.items():
                if isinstance(dict_key, str):
                    try:
                        json.dumps(value)
                        data[dict_key] = value
                    except (TypeError, ValueError):
                        pass
            result[key] = data

    # Check if any valid data was found
    for value in result.values():
        if value is not None:
            return result

    return {"nip11_success": False}


def parse_connection_response(connection_response):
    """
    Parse connection test response data.

    This function processes connection test results and validates
    the response format and data types.

    Args:
        connection_response: Response data from connection test (dict expected)

    Returns:
        dict: Parsed connection metadata with validated fields, or
              {'connection_success': False} if parsing fails
    """
    if not isinstance(connection_response, dict):
        return {"connection_success": False}

    return {
        "connection_success": True,
        "rtt_open": connection_response["rtt_open"],
        "rtt_read": connection_response["rtt_read"],
        "rtt_write": connection_response["rtt_write"],
        "openable": connection_response["openable"],
        "writable": connection_response["writable"],
        "readable": connection_response["readable"],
    }
