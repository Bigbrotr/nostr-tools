"""High-level event fetching utilities."""

import asyncio
import uuid
import json
from typing import AsyncGenerator, List, Optional, Dict, Any
from aiohttp import ClientSession, WSMsgType, TCPConnector
from aiohttp_socks import ProxyConnector

from ..core.event import Event
from ..core.relay import Relay
from ..exceptions.errors import RelayConnectionError


async def fetch_events(
    relay: Relay,
    ids: Optional[List[str]] = None,
    authors: Optional[List[str]] = None,
    kinds: Optional[List[int]] = None,
    tags: Optional[Dict[str, List[str]]] = None,
    since: Optional[int] = None,
    until: Optional[int] = None,
    limit: Optional[int] = None,
    socks5_proxy_url: Optional[str] = None,
    timeout: int = 10
) -> List[Event]:
    """
    Fetch events from a relay with the given filters.

    Args:
        relay: Relay to fetch from
        ids: List of event IDs to fetch
        authors: List of author public keys
        kinds: List of event kinds
        tags: Dictionary of tag filters (e.g., {"p": ["pubkey1", "pubkey2"]})
        since: Unix timestamp, events newer than this
        until: Unix timestamp, events older than this
        limit: Maximum number of events to return
        socks5_proxy_url: SOCKS5 proxy URL for Tor relays
        timeout: Request timeout in seconds

    Returns:
        List of events fetched from the relay

    Raises:
        RelayConnectionError: If connection or fetching fails

    Example:
        >>> relay = Relay("wss://relay.damus.io")
        >>> events = await fetch_events(relay, kinds=[1], limit=10)
        >>> print(f"Fetched {len(events)} events")
    """
    events = []

    # Build filter
    event_filter = {}
    if ids:
        event_filter["ids"] = ids
    if authors:
        event_filter["authors"] = authors
    if kinds:
        event_filter["kinds"] = kinds
    if tags:
        for tag, values in tags.items():
            event_filter[f"#{tag}"] = values
    if since:
        event_filter["since"] = since
    if until:
        event_filter["until"] = until
    if limit:
        event_filter["limit"] = limit

    subscription_id = str(uuid.uuid4())
    request = json.dumps(["REQ", subscription_id, event_filter])

    # Choose connector
    if relay.network == 'tor':
        if not socks5_proxy_url:
            raise RelayConnectionError(
                "SOCKS5 proxy URL required for Tor relays")
        connector = ProxyConnector.from_url(socks5_proxy_url, force_close=True)
    else:
        connector = TCPConnector(force_close=True)

    try:
        async with ClientSession(connector=connector) as session:
            async with session.ws_connect(relay.url, timeout=timeout) as ws:
                # Send subscription request
                await ws.send_str(request)

                # Listen for events
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=timeout * 10)
                    except asyncio.TimeoutError:
                        break

                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                        except json.JSONDecodeError:
                            continue

                        if data[0] == "EVENT" and data[1] == subscription_id:
                            try:
                                event = Event.from_dict(data[2])
                                events.append(event)
                            except Exception:
                                continue  # Skip invalid events
                        elif data[0] == "EOSE" and data[1] == subscription_id:
                            # End of stored events
                            await ws.send_str(json.dumps(["CLOSE", subscription_id]))
                            await asyncio.sleep(1)
                            break
                        elif data[0] == "CLOSED" and data[1] == subscription_id:
                            break
                        elif data[0] == "NOTICE":
                            continue  # Ignore notices
                    elif msg.type == WSMsgType.ERROR:
                        raise RelayConnectionError(
                            f"WebSocket error: {msg.data}")
                    elif msg.type == WSMsgType.CLOSED:
                        break
                    else:
                        break

    except Exception as e:
        raise RelayConnectionError(
            f"Failed to fetch events from {relay.url}: {e}")

    return events


async def fetch_events_from_multiple_relays(
    relays: List[Relay],
    filters: Dict[str, Any],
    socks5_proxy_url: Optional[str] = None,
    timeout: int = 10,
    max_concurrent: int = 10
) -> Dict[str, List[Event]]:
    """
    Fetch events from multiple relays concurrently.

    Args:
        relays: List of relays to fetch from
        filters: Event filters to apply
        socks5_proxy_url: SOCKS5 proxy URL for Tor relays
        timeout: Request timeout in seconds
        max_concurrent: Maximum concurrent connections

    Returns:
        Dictionary mapping relay URL to list of events

    Example:
        >>> relays = [Relay("wss://relay1.com"), Relay("wss://relay2.com")]
        >>> filters = {"kinds": [1], "limit": 10}
        >>> results = await fetch_events_from_multiple_relays(relays, filters)
        >>> for url, events in results.items():
        ...     print(f"{url}: {len(events)} events")
    """
    async def fetch_from_relay(relay: Relay) -> tuple[str, List[Event]]:
        try:
            events = await fetch_events(
                relay=relay,
                ids=filters.get("ids"),
                authors=filters.get("authors"),
                kinds=filters.get("kinds"),
                tags={k[1:]: v for k, v in filters.items() if k.startswith("#")},
                since=filters.get("since"),
                until=filters.get("until"),
                limit=filters.get("limit"),
                socks5_proxy_url=socks5_proxy_url,
                timeout=timeout
            )
            return relay.url, events
        except Exception:
            return relay.url, []

    # Limit concurrent connections
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(relay: Relay):
        async with semaphore:
            return await fetch_from_relay(relay)

    # Execute all fetches concurrently
    tasks = [fetch_with_semaphore(relay) for relay in relays]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Build results dictionary
    relay_events = {}
    for result in results:
        if isinstance(result, tuple):
            url, events = result
            relay_events[url] = events
        else:
            # Handle exceptions
            continue

    return relay_events


async def stream_events(
    relay: Relay,
    filters: Dict[str, Any],
    socks5_proxy_url: Optional[str] = None,
    timeout: int = 10
) -> AsyncGenerator[Event, None]:
    """
    Stream events from a relay in real-time.

    Args:
        relay: Relay to stream from
        filters: Event filters
        socks5_proxy_url: SOCKS5 proxy URL for Tor relays
        timeout: Connection timeout

    Yields:
        Events as they arrive

    Example:
        >>> relay = Relay("wss://relay.damus.io")
        >>> filters = {"kinds": [1]}
        >>> async for event in stream_events(relay, filters):
        ...     print(f"New event: {event.content}")
    """
    subscription_id = str(uuid.uuid4())
    request = json.dumps(["REQ", subscription_id, filters])

    # Choose connector
    if relay.network == 'tor':
        if not socks5_proxy_url:
            raise RelayConnectionError(
                "SOCKS5 proxy URL required for Tor relays")
        connector = ProxyConnector.from_url(socks5_proxy_url, force_close=True)
    else:
        connector = TCPConnector(force_close=True)

    try:
        async with ClientSession(connector=connector) as session:
            async with session.ws_connect(relay.url, timeout=timeout) as ws:
                # Send subscription request
                await ws.send_str(request)

                # Stream events
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=timeout * 10)
                    except asyncio.TimeoutError:
                        continue

                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                        except json.JSONDecodeError:
                            continue

                        if data[0] == "EVENT" and data[1] == subscription_id:
                            try:
                                event = Event.from_dict(data[2])
                                yield event
                            except Exception:
                                continue  # Skip invalid events
                        elif data[0] == "EOSE" and data[1] == subscription_id:
                            continue  # Keep streaming after EOSE
                        elif data[0] == "CLOSED" and data[1] == subscription_id:
                            break
                        elif data[0] == "NOTICE":
                            continue  # Ignore notices
                    elif msg.type == WSMsgType.ERROR:
                        raise RelayConnectionError(
                            f"WebSocket error: {msg.data}")
                    elif msg.type == WSMsgType.CLOSED:
                        break
                    else:
                        continue

    except Exception as e:
        raise RelayConnectionError(
            f"Failed to stream events from {relay.url}: {e}")
