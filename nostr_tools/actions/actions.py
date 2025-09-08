"""
Actions module providing high-level functions to interact with Nostr relays.
"""

from typing import AsyncGenerator, List

from ..core.event import Event
from ..core.client import Client
from ..core.filter import Filter


async def fetch_events(
    client: Client,
    filter: Filter
) -> List[Event]:
    """
    Fetch events matching the filter using an existing client connection.
    Args:
        client: An instance of Client already connected to a relay
        filter: A Filter instance defining the criteria for fetching events
    Returns:
        A list of Event instances matching the filter
    """
    events = []
    subscription_id = await client.subscribe(filter)
    async for event in client.listen_events(subscription_id):
        events.append(event)
    await client.unsubscribe(subscription_id)
    return events


async def stream_events(
    client: Client,
    filter: Filter
) -> AsyncGenerator[Event, None]:
    """
    Stream events matching the filter using an existing client connection.
    Args:
        client: An instance of Client already connected to a relay
        filter: A Filter instance defining the criteria for streaming events
    Yields:
        Event instances matching the filter as they arrive
    """
    subscription_id = await client.subscribe(filter)
    async for event in client.listen_events(subscription_id):
        yield event
    await client.unsubscribe(subscription_id)
