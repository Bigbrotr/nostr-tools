"""
Actions module providing high-level functions to interact with Nostr relays.
"""

from typing import AsyncGenerator, List, Callable, Dict, Any, Optional
import time
from ..core.event import Event
from ..core.relay_metadata import RelayMetadata
from ..core.client import Client
from ..core.filter import Filter
from ..exceptions.errors import RelayConnectionError
from ..utils import generate_event, parse_nip11_response, parse_connection_response


async def fetch_events(
    client: Client,
    filter: Filter,
    event_handler: Callable[[Dict[str, Any]], Event] = Event.event_handler
) -> List[Event]:
    """
    Fetch events matching the filter using an existing client connection.
    Args:
        client: An instance of Client already connected to a relay
        filter: A Filter instance defining the criteria for fetching events
    Returns:
        A list of Event instances matching the filter
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")
    events = []
    subscription_id = await client.subscribe(filter)
    async for event_message in client.listen_events(subscription_id):
        try:
            event = event_handler(event_message[2])
            events.append(event)
        except Exception:
            continue  # Skip invalid events
    await client.unsubscribe(subscription_id)
    return events


async def stream_events(
    client: Client,
    filter: Filter,
    event_handler: Callable[[Dict[str, Any]], Event] = Event.event_handler
) -> AsyncGenerator[Event, None]:
    """
    Stream events matching the filter using an existing client connection.
    Args:
        client: An instance of Client already connected to a relay
        filter: A Filter instance defining the criteria for streaming events
    Yields:
        Event instances matching the filter as they arrive
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")
    subscription_id = await client.subscribe(filter)
    async for event_message in client.listen_events(subscription_id):
        try:
            event = event_handler(event_message[2])
            yield event
        except Exception:
            continue  # Skip invalid events
    await client.unsubscribe(subscription_id)


async def fetch_nip11(client: Client):
    """
    Fetch NIP-11 metadata from the relay.
    Args:
        client: An instance of Client
    Returns:
        Dictionary containing NIP-11 metadata or None if not available
    """
    relay_id = client.relay.url.removeprefix('wss://')
    headers = {'Accept': 'application/nostr+json'}
    for schema in ['https://', 'http://']:
        try:
            async with client.session() as session:
                async with session.get(schema + relay_id, headers=headers, timeout=client.timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        pass
        except Exception:
            pass
    return None


async def check_connectivity(client: Client):
    """
    Check if the relay is connectable.
    Args:
        client: An instance of Client
    Returns:
        Tuple of (rtt_open in ms or None, openable as bool)
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


async def check_readability(client: Client):
    """
    Check if the relay is readable.
    Args:
        client: An instance of Client
    Returns:
        Tuple of (rtt_read in ms or None, readable as bool)
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")
    rtt_read = None
    readable = False
    try:
        filter = Filter(limit=1)
        time_start = time.perf_counter()
        subscription_id = await client.subscribe(filter)
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


async def check_writability(client: Client, sec: str, pub: str, target_difficulty: Optional[int] = None, event_creation_timeout: Optional[int] = None):
    """
    Check if the relay is writable.
    Args:
        client: An instance of Client
        sec: The sec parameter for the event
        pub: The pub parameter for the event
        target_difficulty: The target difficulty for the event
        event_creation_timeout: Timeout for event creation
    Returns:
        Tuple of (rtt_write in ms or None, writable as bool)
    """
    if not client.is_connected:
        raise RelayConnectionError("Client is not connected")
    rtt_write = None
    writable = False
    try:
        event = generate_event(
            sec,
            pub,
            30166,
            [["d", client.relay.url]],
            "{}",
            target_difficulty=target_difficulty,
            timeout=event_creation_timeout or client.timeout*10
        )
        time_start = time.perf_counter()
        writable = client.publish(event)
        time_end = time.perf_counter()
        rtt_write = int((time_end - time_start) * 1000)
    except Exception:
        pass
    return rtt_write, writable


async def fetch_connection(client: Client, sec: str, pub: str, target_difficulty: Optional[int] = None, event_creation_timeout: Optional[int] = None):
    """
    Fetch connection metrics from the relay.
    Args:
        client: An instance of Client
        sec: The sec parameter for the event
        pub: The pub parameter for the event
        target_difficulty: The target difficulty for the event
        event_creation_timeout: Timeout for event creation
    Returns:
        Dictionary containing connection metrics or None if not connectable
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
        rtt_open, openable = await check_connectivity(client)
        if not openable:
            return None
        async with client:
            rtt_read, readable = await check_readability(client)
            rtt_write, writable = await check_writability(client, sec, pub, target_difficulty, event_creation_timeout)
        return {
            'rtt_open': rtt_open,
            'rtt_read': rtt_read,
            'rtt_write': rtt_write,
            'openable': openable,
            'writable': writable,
            'readable': readable
        }
    except Exception:
        return None


async def compute_relay_metadata(client: Client, sec: str, pub: str) -> RelayMetadata:
    if client.is_connected:
        raise RelayConnectionError("Client is already connected")
    nip11_response = await fetch_nip11(client)
    nip11_metadata = parse_nip11_response(nip11_response)
    target_difficulty = nip11_metadata.get('limitation', {})
    target_difficulty = None if not isinstance(
        target_difficulty, dict) else target_difficulty.get('min_pow_difficulty')
    target_difficulty = target_difficulty if isinstance(
        target_difficulty, int) else None
    connection_response = await fetch_connection(client, sec, pub, target_difficulty)
    connection_metadata = parse_connection_response(connection_response)
    metadata = {
        'relay': client.relay.url,
        'generated_at': int(time.time()),
        **nip11_metadata,
        **connection_metadata
    }
    return RelayMetadata.from_dict(metadata)
