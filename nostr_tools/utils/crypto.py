"""Cryptographic utilities for Nostr protocol."""

import hashlib
import json
import time
import secrets
from typing import List, Optional, Dict, Any
import secp256k1
import bech32


def calc_event_id(pubkey: str, created_at: int, kind: int, tags: List[List[str]], content: str) -> str:
    """
    Calculate the event ID for a Nostr event.

    Args:
        pubkey: Public key in hex format
        created_at: Unix timestamp
        kind: Event kind
        tags: List of tags
        content: Event content

    Returns:
        Event ID as hex string
    """
    event_data = [0, pubkey, created_at, kind, tags, content]
    event_json = json.dumps(
        event_data, separators=(',', ':'), ensure_ascii=False)
    event_bytes = event_json.encode('utf-8')
    event_hash = hashlib.sha256(event_bytes).digest()
    return event_hash.hex()


def verify_sig(event_id: str, pubkey: str, signature: str) -> bool:
    """
    Verify an event signature.

    Args:
        event_id: Event ID in hex format
        pubkey: Public key in hex format  
        signature: Signature in hex format

    Returns:
        True if signature is valid
    """
    try:
        # Convert hex strings to bytes
        event_id_bytes = bytes.fromhex(event_id)
        pubkey_bytes = bytes.fromhex(pubkey)
        signature_bytes = bytes.fromhex(signature)

        # Create public key object
        pubkey_obj = secp256k1.PublicKey(pubkey_bytes, raw=True)

        # Verify signature
        return pubkey_obj.ecdsa_verify(event_id_bytes, signature_bytes, raw=True)
    except Exception:
        return False


def generate_event(
    private_key: str,
    public_key: str,
    kind: int,
    tags: List[List[str]],
    content: str,
    created_at: Optional[int] = None,
    target_difficulty: int = 0,
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Generate a signed Nostr event.

    Args:
        private_key: Private key in hex format
        public_key: Public key in hex format
        kind: Event kind
        tags: List of tags
        content: Event content
        created_at: Unix timestamp (defaults to current time)
        target_difficulty: Proof of work difficulty target
        timeout: Timeout for proof of work in seconds

    Returns:
        Complete signed event as dictionary
    """
    if created_at is None:
        created_at = int(time.time())

    # Generate proof of work if required
    if target_difficulty > 0:
        nonce_tag = None
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Proof of work generation timed out")

            # Generate random nonce
            nonce = secrets.token_hex(16)

            # Create temporary tags with nonce
            temp_tags = tags + [["nonce", nonce, str(target_difficulty)]]

            # Calculate event ID
            event_id = calc_event_id(
                public_key, created_at, kind, temp_tags, content)

            # Check if difficulty target is met
            if event_id.startswith('0' * target_difficulty):
                tags = temp_tags
                break

    # Calculate final event ID
    event_id = calc_event_id(public_key, created_at, kind, tags, content)

    # Sign the event
    private_key_bytes = bytes.fromhex(private_key)
    event_id_bytes = bytes.fromhex(event_id)

    privkey_obj = secp256k1.PrivateKey(private_key_bytes, raw=True)
    signature = privkey_obj.ecdsa_sign(event_id_bytes, raw=True)
    signature_hex = signature.hex()

    return {
        "id": event_id,
        "pubkey": public_key,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": content,
        "sig": signature_hex
    }


def test_keypair(private_key: str, public_key: str) -> bool:
    """
    Test if a private/public key pair is valid.

    Args:
        private_key: Private key in hex format
        public_key: Public key in hex format

    Returns:
        True if the key pair is valid
    """
    try:
        # Convert private key to bytes
        private_key_bytes = bytes.fromhex(private_key)

        # Create private key object
        privkey_obj = secp256k1.PrivateKey(private_key_bytes, raw=True)

        # Get public key from private key
        derived_pubkey = privkey_obj.pubkey.serialize(compressed=False)[1:]
        derived_pubkey_hex = derived_pubkey.hex()

        return derived_pubkey_hex == public_key
    except Exception:
        return False


def to_bech32(prefix: str, hex_str: str) -> str:
    """
    Convert a hex string to Bech32 format.

    Args:
        prefix: The prefix for the Bech32 encoding (e.g., 'nsec', 'npub')
        hex_str: The hex string to convert

    Returns:
        The Bech32 encoded string
    """
    byte_data = bytes.fromhex(hex_str)
    data = bech32.convertbits(byte_data, 8, 5, True)
    return bech32.bech32_encode(prefix, data)


def to_hex(bech32_str: str) -> str:
    """
    Convert a Bech32 string to hex format.

    Args:
        bech32_str: The Bech32 string to convert

    Returns:
        The hex encoded string
    """
    prefix, data = bech32.bech32_decode(bech32_str)
    byte_data = bech32.convertbits(data, 5, 8, False)
    return bytes(byte_data).hex()


def generate_keypair() -> tuple[str, str]:
    """
    Generate a new private/public key pair.

    Returns:
        Tuple of (private_key_hex, public_key_hex)
    """
    # Generate random private key
    private_key_bytes = secrets.token_bytes(32)

    # Create private key object
    privkey_obj = secp256k1.PrivateKey(private_key_bytes, raw=True)

    # Get public key
    pubkey_bytes = privkey_obj.pubkey.serialize(compressed=False)[1:]

    return private_key_bytes.hex(), pubkey_bytes.hex()
