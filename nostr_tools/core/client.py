"""
WebSocket client for Nostr relays.

This module provides the Client class for establishing WebSocket connections
to Nostr relays, subscribing to events, publishing events, and managing
relay communications.
"""

import asyncio
import json
import uuid
from typing import Optional, Dict, Any, List, AsyncGenerator
from aiohttp import ClientSession, WSMsgType, TCPConnector, ClientTimeout
from aiohttp_socks import ProxyConnector

from .relay import Relay
from .event import Event
from .filter import Filter
from ..exceptions import RelayConnectionError


class Client:
    """
    WebSocket client for connecting to Nostr relays.

    This class provides async methods for subscribing to events, sending events,
    and managing connections with proper error handling. It supports both
    clearnet and Tor relays.

    Attributes:
        relay (Relay): The relay to connect to
        timeout (Optional[int]): Connection timeout in seconds
        socks5_proxy_url (Optional[str]): SOCKS5 proxy URL for Tor relays
    """

    def __init__(
        self,
        relay: Relay,
        timeout: Optional[int] = 10,
        socks5_proxy_url: Optional[str] = None
    ):
        """
        Initialize the WebSocket client.

        Args:
            relay (Relay): Relay to connect to
            timeout (Optional[int]): Connection timeout in seconds (default: 10)
            socks5_proxy_url (Optional[str]): SOCKS5 proxy URL for Tor relays

        Raises:
            TypeError: If arguments are of incorrect type
            ValueError: If SOCKS5 proxy URL is required for Tor but not provided
        """
        # Validate input types
        to_validate = [
            ("relay", relay, Relay),
            ("timeout", timeout, (int, type(None))),
            ("socks5_proxy_url", socks5_proxy_url, (str, type(None)))
        ]
        for name, value, types in to_validate:
            if not isinstance(value, types):
                raise TypeError(f"{name} must be of type {types}")
        if relay.network == 'tor' and not socks5_proxy_url:
            raise ValueError(
                "socks5_proxy_url is required for Tor relays")
        self.relay = relay
        self.timeout = timeout
        self.socks5_proxy_url = socks5_proxy_url
        self._session: Optional[ClientSession] = None
        self._ws = None
        self._subscriptions: Dict[str, Dict[str, Any]] = {}

    async def __aenter__(self):
        """
        Async context manager entry.

        Returns:
            Client: Self for use in async with statement
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        await self.disconnect()

    def connector(self):
        """
        Create appropriate connector based on network type.

        Returns:
            Connector: TCPConnector for clearnet or ProxyConnector for Tor

        Raises:
            RelayConnectionError: If SOCKS5 proxy URL required for Tor but not provided
        """
        # Choose connector based on network type
        if self.relay.network == 'tor':
            if not self.socks5_proxy_url:
                raise RelayConnectionError(
                    "SOCKS5 proxy URL required for Tor relays")
            connector = ProxyConnector.from_url(
                self.socks5_proxy_url, force_close=True)
        else:
            connector = TCPConnector(force_close=True)
        return connector

    def session(self, connector=None):
        """
        Create HTTP session with specified connector.

        Args:
            connector: Optional connector to use (default: auto-detect)

        Returns:
            ClientSession: HTTP session for making requests
        """
        if connector is None:
            connector = self.connector()
        return ClientSession(connector=connector)

    async def connect(self) -> None:
        """
        Establish WebSocket connection to the relay.

        This method attempts to connect using both WSS and WS protocols,
        preferring WSS for security.

        Raises:
            RelayConnectionError: If connection fails
        """
        if self.is_connected:
            return  # Already connected

        try:
            connector = self.connector()
            self._session = self.session(connector=connector)
            relay_id = self.relay.url.removeprefix('wss://')
            timeout = ClientTimeout(total=self.timeout) if self.timeout else None
            # Try both WSS and WS protocols
            for schema in ['wss://', 'ws://']:
                try:
                    self._ws = await self._session.ws_connect(schema + relay_id, timeout=timeout)
                    break
                except Exception:
                    continue

            if not self._ws or self._ws.closed:
                raise Exception("Failed to establish WebSocket connection")

        except Exception as e:
            if self._session:
                await self._session.close()
                self._session = None
            raise RelayConnectionError(
                f"Failed to connect to {self.relay.url}: {e}")

    async def disconnect(self) -> None:
        """
        Close WebSocket connection and cleanup resources.

        This method properly closes the WebSocket connection, HTTP session,
        and clears all active subscriptions.
        """
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
            message (List[Any]): Message to send as a list (will be JSON encoded)

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
        filter: Filter,
        subscription_id: Optional[str] = None
    ) -> str:
        """
        Subscribe to events matching the given filter.

        Args:
            filter (Filter): Event filter criteria
            subscription_id (Optional[str]): Optional subscription ID (auto-generated if None)

        Returns:
            str: Subscription ID for managing the subscription

        Raises:
            RelayConnectionError: If subscription fails
        """
        if subscription_id is None:
            subscription_id = str(uuid.uuid4())

        request = ["REQ", subscription_id, filter.filter_dict]
        await self.send_message(request)

        self._subscriptions[subscription_id] = {
            "filter": filter,
            "active": True
        }

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> None:
        """
        Unsubscribe from events.

        Args:
            subscription_id (str): Subscription ID to close
        """
        if subscription_id in self._subscriptions:
            request = ["CLOSE", subscription_id]
            await self.send_message(request)
            self._subscriptions[subscription_id]["active"] = False

    async def publish(self, event: Event) -> bool:
        """
        Publish an event to the relay.

        Args:
            event (Event): Event to publish

        Returns:
            bool: True if accepted by relay, False otherwise

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

    async def authenticate(self, event: Event) -> bool:
        """
        Authenticate with the relay using a NIP-42 event.

        Args:
            event (Event): Authentication event (must be kind 22242)

        Returns:
            bool: True if authentication successful, False otherwise

        Raises:
            ValueError: If event kind is not 22242
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

        This method continuously listens for messages from the relay
        and yields them as they arrive.

        Yields:
            List[Any]: Messages received from relay

        Raises:
            RelayConnectionError: If connection fails or encounters errors
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
    ) -> AsyncGenerator[List[Any], None]:
        """
        Listen for events from a specific subscription.

        This method filters messages to only yield events from the
        specified subscription until the subscription ends.

        Args:
            subscription_id (str): Subscription to listen to

        Yields:
            List[Any]: Events received from the subscription
        """
        async for message in self.listen():
            if message[0] == "EVENT" and message[1] == subscription_id:
                yield message
            elif message[0] == "EOSE" and message[1] == subscription_id:
                break  # End of stored events
            elif message[0] == "CLOSED" and message[1] == subscription_id:
                break  # Subscription closed
            elif message[0] == "NOTICE":
                continue  # Ignore notices

    @property
    def is_connected(self) -> bool:
        """
        Check if client is connected to the relay.

        Returns:
            bool: True if connected, False otherwise
        """
        return self._ws is not None and not self._ws.closed

    @property
    def active_subscriptions(self) -> List[str]:
        """
        Get list of active subscription IDs.

        Returns:
            List[str]: List of subscription IDs that are currently active
        """
        return [
            sub_id for sub_id, sub_data in self._subscriptions.items()
            if sub_data["active"]
        ]
