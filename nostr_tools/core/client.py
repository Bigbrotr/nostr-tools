"""WebSocket client for Nostr relays."""

import asyncio
import json
import uuid
from typing import Optional, Dict, Any, List, AsyncGenerator
from aiohttp import ClientSession, WSMsgType, TCPConnector
from aiohttp_socks import ProxyConnector

from .relay import Relay
from .event import Event
from ..exceptions import RelayConnectionError


class Client:
    """
    WebSocket client for connecting to Nostr relays.

    Provides async methods for subscribing to events, sending events,
    and managing connections with proper error handling.
    """

    def __init__(
        self,
        relay: Relay,
        timeout: int = 10,
        socks5_proxy_url: Optional[str] = None
    ):
        """
        Initialize the WebSocket client.

        Args:
            relay: Relay to connect to
            timeout: Connection timeout in seconds
            socks5_proxy_url: SOCKS5 proxy URL for Tor relays
        """
        self.relay = relay
        self.timeout = timeout
        self.socks5_proxy_url = socks5_proxy_url
        self._session: Optional[ClientSession] = None
        self._ws = None
        self._subscriptions: Dict[str, Dict[str, Any]] = {}

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> None:
        """Establish WebSocket connection to the relay."""
        if self._session is not None:
            return  # Already connected

        # Choose connector based on network type
        if self.relay.network == 'tor':
            if not self.socks5_proxy_url:
                raise RelayConnectionError(
                    "SOCKS5 proxy URL required for Tor relays")
            connector = ProxyConnector.from_url(
                self.socks5_proxy_url, force_close=True)
        else:
            connector = TCPConnector(force_close=True)

        try:
            self._session = ClientSession(connector=connector)
            self._ws = await self._session.ws_connect(self.relay.url, timeout=self.timeout)
        except Exception as e:
            if self._session:
                await self._session.close()
                self._session = None
            raise RelayConnectionError(
                f"Failed to connect to {self.relay.url}: {e}")

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        if self._ws:
            await self._ws.close()
            self._ws = None

        if self._session:
            await self._session.close()
            self._session = None

        self._subscriptions.clear()

    async def send_message(self, message: List[Any]) -> None:
        """
        Send a message to the relay.

        Args:
            message: Message to send as a list

        Raises:
            RelayConnectionError: If not connected or send fails
        """
        if not self._ws:
            raise RelayConnectionError("Not connected to relay")

        try:
            await self._ws.send_str(json.dumps(message))
        except Exception as e:
            raise RelayConnectionError(f"Failed to send message: {e}")

    async def subscribe(
        self,
        filters: Dict[str, Any],
        subscription_id: Optional[str] = None
    ) -> str:
        """
        Subscribe to events matching the given filters.

        Args:
            filters: Event filters
            subscription_id: Optional subscription ID

        Returns:
            Subscription ID

        Raises:
            RelayConnectionError: If subscription fails
        """
        if subscription_id is None:
            subscription_id = str(uuid.uuid4())

        request = ["REQ", subscription_id, filters]
        await self.send_message(request)

        self._subscriptions[subscription_id] = {
            "filters": filters,
            "active": True
        }

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> None:
        """
        Unsubscribe from events.

        Args:
            subscription_id: Subscription ID to close
        """
        if subscription_id in self._subscriptions:
            request = ["CLOSE", subscription_id]
            await self.send_message(request)
            self._subscriptions[subscription_id]["active"] = False

    async def publish(self, event: Event) -> bool:
        """
        Publish an event to the relay.

        Args:
            event: Event to publish

        Returns:
            True if accepted by relay

        Raises:
            RelayConnectionError: If publish fails
        """
        request = ["EVENT", event.to_dict()]
        await self.send_message(request)

        # Wait for OK response
        async for message in self.listen():
            if message[0] == "OK" and message[1] == event.id:
                return message[2]  # Success flag
            elif message[0] == "NOTICE":
                continue  # Ignore notices

        return False

    async def authenticate(self, event: Event) -> None:
        """
        Authenticate with the relay using a NIP-42 event.

        Args:
            event: Authentication event

        Raises:
            RelayConnectionError: If authentication fails
        """
        if event.kind != 22242:
            raise ValueError("Event kind must be 22242 for authentication")

        request = ["AUTH", event.to_dict()]
        await self.send_message(request)

        # Wait for OK response
        async for message in self.listen():
            if message[0] == "OK" and message[1] == event.id:
                return message[2]  # Success flag
            elif message[0] == "NOTICE":
                continue

        return False

    async def listen(self) -> AsyncGenerator[List[Any], None]:
        """
        Listen for messages from the relay.

        Yields:
            Messages received from relay

        Raises:
            RelayConnectionError: If connection fails
        """
        if not self._ws:
            raise RelayConnectionError("Not connected to relay")

        try:
            while True:
                msg = await asyncio.wait_for(self._ws.receive(), timeout=self.timeout)

                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        yield data
                    except json.JSONDecodeError:
                        continue
                elif msg.type == WSMsgType.ERROR:
                    raise RelayConnectionError(f"WebSocket error: {msg.data}")
                elif msg.type == WSMsgType.CLOSED:
                    break
                else:
                    raise RelayConnectionError(
                        f"Unexpected message type: {msg.type}")

        except asyncio.TimeoutError:
            pass
        except Exception as e:
            raise RelayConnectionError(f"Error listening to relay: {e}")

    async def listen_events(
        self,
        subscription_id: str,
    ) -> AsyncGenerator[Event, None]:
        """
        Listen for events from a specific subscription.

        Args:
            subscription_id: Subscription to listen to
            event_handler: Optional event handler function

        Yields:
            Events received from the subscription
        """
        async for message in self.listen():
            if message[0] == "EVENT" and message[1] == subscription_id:
                try:
                    event = Event.from_dict(message[2])
                    yield event
                except Exception:
                    continue  # Skip invalid events
            elif message[0] == "EOSE" and message[1] == subscription_id:
                break  # End of stored events
            elif message[0] == "CLOSED" and message[1] == subscription_id:
                break  # Subscription closed
            elif message[0] == "NOTICE":
                continue  # Ignore notices

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._ws is not None and not self._ws.closed

    @property
    def active_subscriptions(self) -> List[str]:
        """Get list of active subscription IDs."""
        return [
            sub_id for sub_id, sub_data in self._subscriptions.items()
            if sub_data["active"]
        ]
