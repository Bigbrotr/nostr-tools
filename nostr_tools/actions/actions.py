"""
Actions module providing high-level functions to interact with Nostr relays.

This module contains functions for fetching events, streaming data, testing
relay capabilities, and computing comprehensive relay metadata. These functions
provide a high-level interface for common Nostr protocol operations.

The main categories of actions include:

Event Operations:
    - fetch_events: Retrieve stored events matching filter criteria
    - stream_events: Continuously stream events as they arrive

Relay Information:
    - fetch_nip11: Retrieve NIP-11 relay information document
    - check_connectivity: Test basic WebSocket connection capability
    - check_readability: Test ability to subscribe and receive events
    - check_writability: Test ability to publish events
    - fetch_connection: Perform complete connection capability analysis
    - compute_relay_metadata: Generate comprehensive relay metadata

All functions work with existing Client instances and handle errors gracefully.
Connection testing functions automatically detect proof-of-work requirements
from relay NIP-11 metadata when available.

Example:
    Basic usage of action functions:

    >>> # Create relay and client
    >>> relay = Relay("wss://relay.damus.io")
    >>> client = Client(relay)

    >>> # Test relay capabilities
    >>> metadata = await compute_relay_metadata(client, private_key, public_key)
    >>> print(f"Relay is {'readable' if metadata.readable else 'not readable'}")

    >>> # Fetch events
    >>> async with client:
    ...     filter = Filter(kinds=[1], limit=10)
    ...     events = await fetch_events(client, filter)
    ...     print(f"Retrieved {len(events)} events")

    >>> # Stream events continuously
    >>> async with client:
    ...     filter = Filter(kinds=[1])
    ...     async for event in stream_events(client, filter):
    ...         print(f"New event: {event.content}")
"""

from collections.abc import AsyncGenerator
import time
from typing import Any, Optional

from ..core.client import Client
from ..core.event import Event
from ..core.filter import Filter
from ..core.relay_metadata import RelayMetadata
from ..exceptions.errors import RelayConnectionError
from ..utils import generate_event, parse_connection_response, parse_nip11_response


async def fetch_events(
    client: Client,
    filter: Filter,
) -> list[Event]:
    """
    Fetch events matching the filter using an existing client connection.

    This function subscribes to events matching the filter criteria, collects
    all matching events, and returns them as a list. The subscription is
    automatically closed when all stored events have been received.

    Args:
        client (Client): An instance of Client already connected to a relay
        filter (Filter): A Filter instance defining the criteria for fetching events

    Returns:
        List[Event]: A list of Event instances matching the filter

    Raises:
        RelayConnectionError: If client is not connected
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")

    events = []
    subscription_id = await client.subscribe(filter)

    # Listen for events until end of stored events (EOSE)
    async for event_message in client.listen_events(subscription_id):
        try:
            event = Event.from_dict(event_message[2])
            events.append(event)
        except Exception:
            continue  # Skip invalid events

    await client.unsubscribe(subscription_id)
    return events


async def stream_events(
    client: Client,
    filter: Filter,
) -> AsyncGenerator[Event, None]:
    """
    Stream events matching the filter using an existing client connection.

    This function subscribes to events and yields them as they arrive from
    the relay. Unlike fetch_events, this continues indefinitely and yields
    both stored and new events.

    Args:
        client (Client): An instance of Client already connected to a relay
        filter (Filter): A Filter instance defining the criteria for streaming events

    Yields:
        Event: Event instances matching the filter as they arrive

    Raises:
        RelayConnectionError: If client is not connected
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")

    subscription_id = await client.subscribe(filter)

    # Stream events continuously
    async for event_message in client.listen_events(subscription_id):
        try:
            event = Event.from_dict(event_message[2])
            yield event
        except Exception:
            continue  # Skip invalid events

    await client.unsubscribe(subscription_id)


async def fetch_nip11(client: Client) -> Optional[dict[str, Any]]:
    """
    Fetch NIP-11 metadata from the relay.

    This function attempts to retrieve the NIP-11 relay information document
    by making HTTP requests to the relay's information endpoint. It tries
    both HTTPS and HTTP protocols.

    Args:
        client (Client): An instance of Client (connection not required)

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing NIP-11 metadata or None if not available
    """
    relay_id = client.relay.url.removeprefix("wss://")
    headers = {"Accept": "application/nostr+json"}

    # Try both HTTPS and HTTP protocols
    for schema in ["https://", "http://"]:
        try:
            async with (
                client.session() as session,
                session.get(
                    schema + relay_id, headers=headers, timeout=client.timeout
                ) as response,
            ):
                if response.status == 200:
                    result = await response.json()
                    return dict(result) if isinstance(result, dict) else result
        except Exception:
            pass

    return None


async def check_connectivity(client: Client) -> tuple[Optional[int], bool]:
    """
    Check if the relay is connectable and measure connection time.

    This function attempts to establish a WebSocket connection to the relay
    and measures the round-trip time for the connection establishment.

    Args:
        client (Client): An instance of Client (must not be already connected)

    Returns:
        Tuple[Optional[int], bool]: (rtt_open in ms or None, openable as bool)

    Raises:
        RelayConnectionError: If client is already connected
    """
    if client.is_connected:
        raise RelayConnectionError("Client is already connected")

    rtt_open = None
    openable = False

    try:
        time_start = time.perf_counter()
        async with client:
            time_end = time.perf_counter()
            rtt_open = int((time_end - time_start) * 1000)
            openable = True
    except Exception:
        pass

    return rtt_open, openable


async def check_readability(client: Client) -> tuple[Optional[int], bool]:
    """
    Check if the relay allows reading events and measure read response time.

    This function subscribes to a simple filter and measures how long it takes
    to receive a response (either events or end-of-stored-events).

    Args:
        client (Client): An instance of Client (must be connected)

    Returns:
        Tuple[Optional[int], bool]: (rtt_read in ms or None, readable as bool)

    Raises:
        RelayConnectionError: If client is not connected
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")

    rtt_read = None
    readable = False

    try:
        filter = Filter(limit=1)
        time_start = time.perf_counter()
        subscription_id = await client.subscribe(filter)

        # Listen for first response to measure read capability
        async for message in client.listen():
            if rtt_read is None:
                time_end = time.perf_counter()
                rtt_read = int((time_end - time_start) * 1000)

            if message[0] == "EVENT" and message[1] == subscription_id:
                readable = True
                break
            elif message[0] == "EOSE" and message[1] == subscription_id:
                readable = True
                break  # End of stored events
            elif message[0] == "CLOSED" and message[1] == subscription_id:
                break  # Subscription closed
            elif message[0] == "NOTICE":
                continue  # Ignore notices

        await client.unsubscribe(subscription_id)
    except Exception:
        pass

    return rtt_read, readable


async def check_writability(
    client: Client,
    sec: str,
    pub: str,
    target_difficulty: Optional[int] = None,
    event_creation_timeout: Optional[int] = None,
) -> tuple[Optional[int], bool]:
    """
    Check if the relay allows writing events and measure write response time.

    This function creates and publishes a test event (kind 30166) to the relay
    and measures the response time. The event uses the relay URL as identifier.

    Args:
        client (Client): An instance of Client (must be connected)
        sec (str): Private key for signing the test event
        pub (str): Public key corresponding to the private key
        target_difficulty (Optional[int]): Proof-of-work difficulty for the event
        event_creation_timeout (Optional[int]): Timeout for event creation

    Returns:
        Tuple[Optional[int], bool]: (rtt_write in ms or None, writable as bool)

    Raises:
        RelayConnectionError: If client is not connected
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")

    rtt_write = None
    writable = False

    try:
        # Generate test event with relay URL as identifier
        timeout = (
            event_creation_timeout
            if event_creation_timeout is not None
            else (client.timeout or 10)
        )

        event_dict = generate_event(
            sec,
            pub,
            30166,  # Parameterized replaceable event kind
            [["d", client.relay.url]],  # 'd' tag for identifier
            "{}",  # Empty JSON content
            target_difficulty=target_difficulty,
            timeout=timeout,
        )
        event = Event.from_dict(event_dict)

        # Measure publish response time
        time_start = time.perf_counter()
        writable = await client.publish(event)
        time_end = time.perf_counter()
        rtt_write = int((time_end - time_start) * 1000)
    except Exception:
        pass

    return rtt_write, writable


async def fetch_connection(
    client: Client,
    sec: str,
    pub: str,
    target_difficulty: Optional[int] = None,
    event_creation_timeout: Optional[int] = None,
) -> Optional[dict[str, Any]]:
    """
    Fetch comprehensive connection metrics from the relay.

    This function performs a complete connectivity test including connection
    establishment, read capability testing, and write capability testing.

    Args:
        client (Client): An instance of Client (must not be already connected)
        sec (str): Private key for signing test events
        pub (str): Public key corresponding to the private key
        target_difficulty (Optional[int]): Proof-of-work difficulty for test events
        event_creation_timeout (Optional[int]): Timeout for event creation

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing connection metrics with keys:
                     rtt_open, rtt_read, rtt_write, openable, writable, readable
                     Returns None if connection fails

    Raises:
        RelayConnectionError: If client is already connected
    """
    if client.is_connected:
        raise RelayConnectionError("Client is already connected")

    rtt_open = None
    rtt_read = None
    rtt_write = None
    openable = False
    writable = False
    readable = False

    try:
        # Test basic connectivity first
        rtt_open, openable = await check_connectivity(client)
        if not openable:
            return None

        # Test read and write capabilities while connected
        async with client:
            rtt_read, readable = await check_readability(client)
            rtt_write, writable = await check_writability(
                client, sec, pub, target_difficulty, event_creation_timeout
            )

        return {
            "rtt_open": rtt_open,
            "rtt_read": rtt_read,
            "rtt_write": rtt_write,
            "openable": openable,
            "writable": writable,
            "readable": readable,
        }
    except Exception:
        return None


async def compute_relay_metadata(
    client: Client, sec: str, pub: str, event_creation_timeout: Optional[int] = None
) -> RelayMetadata:
    """
    Compute comprehensive relay metadata including NIP-11 and connection data.

    This function performs a complete relay analysis by fetching NIP-11
    metadata and testing connection capabilities. It automatically detects
    proof-of-work requirements from NIP-11 limitations.

    Args:
        client (Client): An instance of Client (must not be already connected)
        sec (str): Private key for signing test events
        pub (str): Public key corresponding to the private key
        event_creation_timeout (Optional[int]): Timeout for event creation

    Returns:
        RelayMetadata: Complete metadata object for the relay

    Raises:
        RelayConnectionError: If client is already connected
    """
    if client.is_connected:
        raise RelayConnectionError("Client is already connected")

    # Fetch NIP-11 metadata
    nip11_response = await fetch_nip11(client)
    nip11_metadata = parse_nip11_response(nip11_response)

    # Extract proof-of-work difficulty from NIP-11 limitations
    target_difficulty = nip11_metadata.get("limitation", {})
    target_difficulty = (
        None
        if not isinstance(target_difficulty, dict)
        else target_difficulty.get("min_pow_difficulty")
    )
    target_difficulty = (
        target_difficulty if isinstance(target_difficulty, int) else None
    )

    # Test connection capabilities with detected PoW requirement
    connection_response = await fetch_connection(
        client, sec, pub, target_difficulty, event_creation_timeout
    )
    connection_metadata = parse_connection_response(connection_response)

    # Combine all metadata into comprehensive object
    metadata = {
        "relay": client.relay,
        "generated_at": int(time.time()),
        **nip11_metadata,
        **connection_metadata,
    }

    return RelayMetadata.from_dict(metadata)
