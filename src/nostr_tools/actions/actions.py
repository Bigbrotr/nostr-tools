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
    - fetch_nip66: Retrieve comprehensive connection metrics
    - fetch_relay_metadata: Generate comprehensive relay metadata

All functions work with existing Client instances and handle errors gracefully.
Connection testing functions automatically detect proof-of-work requirements
from relay NIP-11 metadata when available.

Example:
    Basic usage of action functions:

    >>> # Create relay and client
    >>> relay = Relay("wss://relay.damus.io")
    >>> client = Client(relay)

    >>> # Test relay capabilities
    >>> metadata = await fetch_relay_metadata(client, private_key, public_key)
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

import json
import logging
import time
from asyncio import TimeoutError
from collections.abc import AsyncGenerator
from typing import Optional

from aiohttp import ClientError

from ..core.client import Client
from ..core.event import Event
from ..core.filter import Filter
from ..core.relay_metadata import RelayMetadata
from ..exceptions.errors import ClientConnectionError
from ..exceptions.errors import ClientPublicationError
from ..utils import generate_event

logger = logging.getLogger(__name__)


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
        ClientConnectionError: If client is not connected

    Examples:
        Fetch recent text notes:

        >>> async with Client(relay) as client:
        ...     filter = Filter(kinds=[1], limit=10)
        ...     events = await fetch_events(client, filter)
        ...     print(f"Found {len(events)} events")

        Fetch events from specific author:

        >>> filter = Filter(authors=["abc123..."], kinds=[1, 3])
        >>> events = await fetch_events(client, filter)
        >>> for event in events:
        ...     print(f"Event {event.id}: {event.content[:50]}...")
    """
    if not client.is_connected:
        raise ClientConnectionError("Client is not connected")

    events = []
    subscription_id = await client.subscribe(filter)

    # Listen for events until end of stored events (EOSE)
    async for event_message in client.listen_events(subscription_id):
        try:
            event = Event.from_dict(event_message[2])
            events.append(event)
        except (TypeError, KeyError, ValueError) as e:
            logger.debug(f"Failed to parse event: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error parsing event: {e}")

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
        ClientConnectionError: If client is not connected

    Examples:
        Stream text notes in real-time:

        >>> async with Client(relay) as client:
        ...     filter = Filter(kinds=[1], limit=10)
        ...     async for event in stream_events(client, filter):
        ...         print(f"New note: {event.content}")
        ...         if event.content.startswith("STOP"):
        ...             break

        Stream events from specific authors:

        >>> filter = Filter(authors=["abc123..."], kinds=[1])
        >>> async for event in stream_events(client, filter):
        ...     process_event(event)
    """
    if not client.is_connected:
        raise ClientConnectionError("Client is not connected")

    subscription_id = await client.subscribe(filter)

    # Stream events continuously
    async for event_message in client.listen_events(subscription_id):
        try:
            event = Event.from_dict(event_message[2])
            yield event
        except (TypeError, KeyError, ValueError) as e:
            logger.debug(f"Failed to parse event: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error parsing event: {e}")

    await client.unsubscribe(subscription_id)


async def fetch_nip11(client: Client) -> Optional[RelayMetadata.Nip11]:
    """
    Fetch NIP-11 metadata from the relay.

    This function attempts to retrieve the NIP-11 relay information document
    by making HTTP requests to the relay's information endpoint. It tries
    both HTTPS and HTTP protocols.

    Args:
        client (Client): An instance of Client (connection not required)

    Returns:
        Optional[RelayMetadata.Nip11]: NIP-11 metadata or None if not available
    """
    relay_id = client.relay.url.removeprefix("wss://")
    headers = {"Accept": "application/nostr+json"}

    # Try both HTTPS and HTTP protocols
    for schema in ["https://", "http://"]:
        try:
            session = client.session()
            async with session:
                async with session.get(
                    schema + relay_id, headers=headers, timeout=client.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if not isinstance(data, dict):
                            return None

                        data_processed = {
                            "name": data.get("name"),
                            "description": data.get("description"),
                            "banner": data.get("banner"),
                            "icon": data.get("icon"),
                            "pubkey": data.get("pubkey"),
                            "contact": data.get("contact"),
                            "supported_nips": data.get("supported_nips"),
                            "software": data.get("software"),
                            "version": data.get("version"),
                            "privacy_policy": data.get("privacy_policy"),
                            "terms_of_service": data.get("terms_of_service"),
                            "limitation": data.get("limitation"),
                            "extra_fields": {
                                key: value
                                for key, value in data.items()
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
                            if not (
                                isinstance(data_processed[key], str) or data_processed[key] is None
                            ):
                                data_processed[key] = None

                        # Validate supported_nips list
                        if not isinstance(data_processed["supported_nips"], list):
                            data_processed["supported_nips"] = None
                        else:
                            data_processed["supported_nips"] = [
                                nip
                                for nip in data_processed["supported_nips"]
                                if isinstance(nip, (int, str))
                            ]

                        # Validate dictionary fields
                        dict_fields = ["limitation", "extra_fields"]
                        for key in dict_fields:
                            field_value = data_processed[key]
                            if not isinstance(field_value, dict):
                                data_processed[key] = None
                            else:
                                tmp = {}
                                for dict_key, value in field_value.items():
                                    if isinstance(dict_key, str):
                                        try:
                                            json.dumps(value)
                                            tmp[dict_key] = value
                                        except (TypeError, ValueError):
                                            continue
                                data_processed[key] = tmp

                        for value in data_processed.values():
                            if value is not None:
                                return RelayMetadata.Nip11.from_dict(data_processed)
                    else:
                        logger.debug(
                            f"NIP-11 not found at {schema + relay_id} (status {response.status})"
                        )
                    return None
        except (ClientError, TimeoutError) as e:
            logger.debug(f"Failed to fetch NIP-11 from {schema + relay_id}: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error fetching NIP-11: {e}")
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
            - rtt_open: Connection time in milliseconds, or None if failed
            - openable: True if connection succeeded, False otherwise

    Raises:
        ClientConnectionError: If client is already connected

    Examples:
        Test relay connectivity:

        >>> client = Client(relay)
        >>> rtt, is_openable = await check_connectivity(client)
        >>> if is_openable:
        ...     print(f"Relay is reachable in {rtt}ms")
        ... else:
        ...     print("Relay is not reachable")

        Use in relay testing:

        >>> for relay_url in relay_list:
        ...     client = Client(Relay(relay_url))
        ...     rtt, openable = await check_connectivity(client)
        ...     if openable:
        ...         print(f"{relay_url}: {rtt}ms")
    """
    if client.is_connected:
        raise ClientConnectionError("Client is already connected")

    rtt_open = None
    openable = False

    try:
        time_start = time.perf_counter()
        async with client:
            time_end = time.perf_counter()
            rtt_open = int((time_end - time_start) * 1000)
            openable = True
    except ClientConnectionError as e:
        logger.debug(f"Relay connection error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during connectivity check: {e}")

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
        ClientConnectionError: If client is not connected
    """
    if not client.is_connected:
        raise ClientConnectionError("Client is not connected")

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
    except ClientConnectionError as e:
        logger.debug(f"Relay connection error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during readability check: {e}")

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
        ClientConnectionError: If client is not connected
    """
    if not client.is_connected:
        raise ClientConnectionError("Client is not connected")

    rtt_write = None
    writable = False

    try:
        # Generate test event with relay URL as identifier
        timeout = (
            event_creation_timeout if event_creation_timeout is not None else (client.timeout or 10)
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
        # Now raises ClientPublicationError on failure
        await client.publish(event)
        time_end = time.perf_counter()
        rtt_write = int((time_end - time_start) * 1000)
        writable = True  # If we get here, publish succeeded
    except ClientPublicationError as e:
        logger.debug(f"Publish error: {e}")
        writable = False
    except ClientConnectionError as e:
        logger.debug(f"Relay connection error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during writability check: {e}")

    return rtt_write, writable


async def fetch_nip66(
    client: Client,
    sec: str,
    pub: str,
    target_difficulty: Optional[int] = None,
    event_creation_timeout: Optional[int] = None,
) -> Optional[RelayMetadata.Nip66]:
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
        Optional[RelayMetadata.Nip66]: NIP-66 metadata or None if not available

    Raises:
        ClientConnectionError: If client is already connected
    """
    if client.is_connected:
        raise ClientConnectionError("Client is already connected")

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

        data = {
            "rtt_open": rtt_open,
            "rtt_read": rtt_read,
            "rtt_write": rtt_write,
            "openable": openable,
            "writable": writable,
            "readable": readable,
        }
        return RelayMetadata.Nip66.from_dict(data)
    except ClientConnectionError as e:
        logger.debug(f"Relay connection error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error fetching NIP-66: {e}")
    return None


async def fetch_relay_metadata(
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
        ClientConnectionError: If client is already connected
    """
    if client.is_connected:
        raise ClientConnectionError("Client is already connected")

    # Fetch NIP-11 metadata
    nip11 = await fetch_nip11(client)

    # Extract proof-of-work difficulty from NIP-11 limitations
    if (
        nip11 is not None
        and nip11.limitation is not None
        and "min_pow_difficulty" in nip11.limitation
    ):
        target_difficulty = nip11.limitation["min_pow_difficulty"]
        target_difficulty = target_difficulty if isinstance(target_difficulty, int) else None
    else:
        target_difficulty = None

    # Test connection capabilities with detected PoW requirement
    nip66 = await fetch_nip66(client, sec, pub, target_difficulty, event_creation_timeout)

    # Combine all metadata into comprehensive object
    data = {
        "relay": client.relay.to_dict() if client.relay else None,
        "nip11": nip11.to_dict() if nip11 else None,
        "nip66": nip66.to_dict() if nip66 else None,
        "generated_at": int(time.time()),
    }

    return RelayMetadata.from_dict(data)
