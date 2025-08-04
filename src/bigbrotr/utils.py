import json
import hashlib
import bech32
import secp256k1
import os
import re
import time

# https://data.iana.org/TLD/tlds-alpha-by-domain.txt
TLDS = []
with open(os.path.join(os.path.dirname(__file__), 'tlds.txt'), 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            TLDS.append(line.upper())

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
URI_GENERIC_REGEX = r'''
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
            \d{1,3})                            # Final group of 1–3 digits (e.g., 192.168.0.1)

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
'''


def calc_event_id(pubkey: str, created_at: int, kind: int, tags: list, content: str) -> str:
    """
    Calculate the event ID based on the provided parameters.

    Parameters:
    - pubkey (str): The public key of the user.
    - created_at (int): The timestamp of the event.
    - kind (int): The kind of event.
    - tags (list): A list of tags associated with the event.
    - content (str): The content of the event.

    Example:
    >>> calc_event_id('pubkey', 1234567890, 1, [['tag1', 'tag2']], 'Hello, World!')
    'e41d2f51b631d627f1c5ed83d66e1535ac0f1542a94db987c93f758c364a7600'

    Returns:
    - str: The calculated event ID as a hexadecimal string.

    Raises:
    None
    """
    data = [0, pubkey.lower(), created_at, kind, tags, content]
    data_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()


def sig_event_id(event_id: str, private_key_hex: str) -> str:
    """
    Sign the event ID using the private key.

    Parameters:
    - event_id (str): The event ID to sign.
    - private_key_hex (str): The private key in hexadecimal format.

    Example:
    >>> sign_event_id('d2c3f4e5b6a7c8d9e0f1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3', 'private_key_hex')
    'signature'

    Returns:
    - str: The signature of the event ID.

    Raises:
    None
    """
    private_key = secp256k1.PrivateKey(bytes.fromhex(private_key_hex))
    sig = private_key.schnorr_sign(
        bytes.fromhex(event_id), bip340tag=None, raw=True)
    return sig.hex()


def verify_sig(event_id: str, pubkey: str, sig: str) -> bool:
    """
    Verify the signature of an event ID using the public key.

    Parameters:
    - event_id (str): The event ID to verify.
    - pubkey (str): The public key of the user.
    - sig (str): The signature to verify.

    Example:
    >>> verify_signature('d2c3f4e5b6a7c8d9e0f1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3', 'pubkey', 'signature')
    True

    Returns:
    - bool: True if the signature is valid, False otherwise.

    Raises:
    None
    """
    try:
        pub_key = secp256k1.PublicKey(bytes.fromhex("02" + pubkey), True)
        result = pub_key.schnorr_verify(bytes.fromhex(
            event_id), bytes.fromhex(sig), None, raw=True)
        if result:
            return True
        else:
            return False
    except (ValueError, TypeError) as e:
        return False


def generate_event(sec: str, pub: str, kind: int, tags: list, content: str, created_at: int | None = None, target_difficulty: int | None = None, timeout: int = 20) -> dict:
    """
    Generates an event with a Proof of Work (PoW) attached, based on given parameters.

    Parameters:
    - sec (str): The private key used for signing the event, in hexadecimal format.
    - pub (str): The public key associated with the user, in hexadecimal format.
    - kind (int): The type or category of the event (e.g., 1 for a text note).
    - tags (list): A list of tags associated with the event. The tags can be used for filtering or categorizing the event.
    - content (str): The main content of the event, such as text or other data.
    - created_at (int, optional): A timestamp indicating when the event was created. If None, the current time is used.
    - target_difficulty (int, optional): The difficulty level for the Proof of Work. This defines how many leading zero bits the event's ID must have to be valid. Default is 0.
    - timeout (int, optional): The maximum time in seconds to attempt finding the valid event ID. Default is 10 seconds.

    Example:
    >>> generate_event('private_key_hex', 'public_key_hex', 1, [['tag1', 'tag2']], 'Hello, World!')
    {
        'id': 'e41d2f51b631d627f1c5ed83d66e1535ac0f1542a94db987c93f758c364a7600', 
        'pubkey': 'public_key_hex', 
        'created_at': 1234567890, 
        'kind': 1, 
        'tags': [['tag1', 'tag2']], 
        'content': 'Hello, World!', 
        'sig': 'signature'
    }

    Returns:
    - dict: A dictionary representing the event, containing:
        - id: The event ID, calculated based on the event parameters.
        - pubkey: The public key of the user who generated the event.
        - created_at: The timestamp of the event.
        - kind: The type or category of the event.
        - tags: The list of tags associated with the event.
        - content: The content of the event.
        - sig: The signature of the event ID.

    Raises:
    None
    """
    def count_leading_zero_bits(hex_str):
        bits = 0
        for char in hex_str:
            val = int(char, 16)
            if val == 0:
                bits += 4
            else:
                bits += (4 - val.bit_length())
                break
        return bits
    original_tags = tags.copy()
    created_at = created_at if created_at is not None else int(time.time())
    if target_difficulty is None:
        tags = original_tags
        event_id = calc_event_id(pub, created_at, kind, tags, content)
    else:
        nonce = 0
        non_nonce_tags = [tag for tag in original_tags if tag[0] != "nonce"]
        start_time = time.time()
        while True:
            tags = non_nonce_tags + \
                [["nonce", str(nonce), str(target_difficulty)]]
            event_id = calc_event_id(pub, created_at, kind, tags, content)
            difficulty = count_leading_zero_bits(event_id)
            if difficulty >= target_difficulty:
                break
            if (time.time() - start_time) >= timeout:
                tags = original_tags
                event_id = calc_event_id(pub, created_at, kind, tags, content)
                break
            nonce += 1
    sig = sig_event_id(event_id, sec)
    return {
        "id": event_id,
        "pubkey": pub,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": content,
        "sig": sig
    }


def generate_nostr_keypair():
    private_key = os.urandom(32)
    private_key_obj = secp256k1.PrivateKey(private_key)
    public_key = private_key_obj.pubkey.serialize(compressed=True)[1:]
    private_key_hex = private_key.hex()
    public_key_hex = public_key.hex()
    return private_key_hex, public_key_hex


def test_keypair(seckey, pubkey):
    if len(seckey) != 64 or len(pubkey) != 64:
        return False
    private_key_bytes = bytes.fromhex(seckey)
    private_key_obj = secp256k1.PrivateKey(private_key_bytes)
    generated_public_key = private_key_obj.pubkey.serialize(compressed=True)[
        1:].hex()
    return generated_public_key == pubkey


def to_bech32(prefix, hex_str):
    """
    Convert a hex string to Bech32 format.

    Args:
        prefix (str): The prefix for the Bech32 encoding (e.g., 'nsec', 'npub').
        hex_str (str): The hex string to convert.

    Returns:
        str: The Bech32 encoded string.
    """
    byte_data = bytes.fromhex(hex_str)
    data = bech32.convertbits(byte_data, 8, 5, True)
    return bech32.bech32_encode(prefix, data)


def to_hex(bech32_str):
    """
    Convert a Bech32 string to hex format.

    Args:
        bech32_str (str): The Bech32 string to convert.

    Returns:
        str: The hex encoded string.
    """
    prefix, data = bech32.bech32_decode(bech32_str)
    byte_data = bech32.convertbits(data, 5, 8, False)
    return bytes(byte_data).hex()


def find_websoket_relay_urls(text):
    """
    Find all WebSocket relays in the given text.

    Parameters:
    - text (str): The text to search for WebSocket relays.

    Example:
    >>> text = "Connect to wss://relay.example.com:443 and ws://relay.example.com"
    >>> find_websoket_relay_urls(text)
    ['wss://relay.example.com:443', 'wss://relay.example.com']

    Returns:
    - list: A list of WebSocket relay URLs found in the text.

    Raises:
    None
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
        if scheme not in ["ws", "wss"]:
            continue
        if port and (port < 0 or port > 65535):
            continue
        if domain and domain.lower().endswith(".onion") and (not re.match(r"^([a-z2-7]{16}|[a-z2-7]{56})\.onion$", domain.lower())):
            continue
        if domain and (domain.split(".")[-1].upper() not in TLDS + ["ONION"]):
            continue
        port = ":" + str(port) if port else ""
        url = "wss://" + host.lower() + port + path
        result.append(url)
    return result


def sanitize(value):
    if isinstance(value, str):
        value = value.replace('\x00', '')
    elif isinstance(value, list):
        value = [sanitize(item) for item in value]
    elif isinstance(value, dict):
        value = {sanitize(key): sanitize(val) for key, val in value.items()}
    return value
