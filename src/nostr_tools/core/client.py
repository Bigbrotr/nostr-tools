"""
WebSocket client for Nostr relays.
"""

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from dataclasses import field
from types import TracebackType
from typing import Any
from typing import Optional
from typing import Union

from aiohttp import ClientSession
from aiohttp import ClientWebSocketResponse
from aiohttp import ClientWSTimeout
from aiohttp import TCPConnector
from aiohttp import WSMsgType
from aiohttp_socks import ProxyConnector

from ..exceptions import ClientConnectionError
from ..exceptions import ClientPublicationError
from ..exceptions import ClientSubscriptionError
from ..exceptions import ClientValidationError
from .event import Event
from .filter import Filter
from .relay import Relay

logger = logging.getLogger(__name__)


@dataclass
class Client:
    """
    Async WebSocket client for connecting to Nostr relays.

    This class provides async methods for subscribing to events, publishing events,
    and managing WebSocket connections with proper error handling and timeout support.
    It supports both clearnet and Tor relays via SOCKS5 proxy. The client implements
    async context manager protocol for automatic connection management.

    Examples:
        Basic usage with context manager:

        >>> relay = Relay("wss://relay.damus.io")
        >>> client = Client(relay, timeout=15)
        >>> async with client:
        ...     # Client is automatically connected
        ...     filter = Filter(kinds=[1], limit=10)
        ...     events = await fetch_events(client, filter)

        Connect to Tor relay:

        >>> tor_relay = Relay("wss://relay.onion")
        >>> client = Client(
        ...     relay=tor_relay,
        ...     socks5_proxy_url="socks5://127.0.0.1:9050"
        ... )
        >>> async with client:
        ...     # Use Tor connection
        ...     pass

        Manual connection management:

        >>> client = Client(relay)
        >>> await client.connect()
        >>> try:
        ...     # Perform operations
        ...     sub_id = await client.subscribe(filter)
        ... finally:
        ...     await client.disconnect()

        Subscribe and publish:

        >>> async with client:
        ...     # Subscribe to events
        ...     filter = Filter(kinds=[1], authors=["abc123..."])
        ...     sub_id = await client.subscribe(filter)
        ...
        ...     # Publish an event
        ...     success = await client.publish(event)
        ...
        ...     # Listen for events
        ...     async for message in client.listen_events(sub_id):
        ...         event = Event.from_dict(message[2])
        ...         print(event.content)
        ...         break
        ...
        ...     await client.unsubscribe(sub_id)

    Raises:
        ClientValidationError: If client configuration is invalid (relay type, timeout, proxy).
        ClientConnectionError: If connection to relay fails.
    """

    #: The Nostr relay to connect to. Must be a valid Relay instance with properly formatted WebSocket URL.
    relay: Relay
    #: Connection and operation timeout in seconds. Default is 10 seconds. Set to None for no timeout.
    timeout: Optional[int] = 10
    #: SOCKS5 proxy URL for Tor relays. Required when connecting to .onion relays. Format: "socks5://host:port"
    socks5_proxy_url: Optional[str] = None
    _session: Optional[ClientSession] = field(default=None, init=False)
    _ws: Optional[ClientWebSocketResponse] = field(default=None, init=False)
    _subscriptions: dict[str, dict[str, Any]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """
        Validate Client configuration after initialization.

        This method is automatically called after the dataclass is created.
        It validates all configuration parameters to ensure the client is
        properly configured before use.

        Raises:
            ClientValidationError: If configuration is invalid (negative timeout, missing proxy, etc.).
        """
        self.validate()

    def validate(self) -> None:
        """
        Validate the Client instance configuration.

        Performs comprehensive validation including:
        - Type checking for relay, timeout, and proxy URL
        - Timeout value validation (must be non-negative if set)
        - SOCKS5 proxy requirement check for Tor relays

        Raises:
            ClientValidationError: If any attribute is invalid:
                - relay must be a Relay instance
                - timeout must be int or None and non-negative
                - socks5_proxy_url must be str or None
                - SOCKS5 proxy URL is required for Tor relays

        Examples:
            >>> client = Client(relay, timeout=10)
            >>> client.validate()  # Passes validation

            >>> invalid_client = Client(relay, timeout=-5)
            >>> invalid_client.validate()  # Raises ClientValidationError
        """
        if not (isinstance(self.relay, Relay) or type(self.relay).__name__ == "Relay"):
            raise ClientValidationError(f"relay must be Relay, got {type(self.relay)}")
        if not self.relay.is_valid:
            raise ClientValidationError(f"relay is invalid: {self.relay}")

        if self.timeout is not None and not isinstance(self.timeout, int):
            raise ClientValidationError(f"timeout must be int or None, got {type(self.timeout)}")
        if self.timeout is not None and self.timeout < 0:
            raise ClientValidationError("timeout must be non-negative")

        if self.socks5_proxy_url is not None and not isinstance(self.socks5_proxy_url, str):
            raise ClientValidationError(
                f"socks5_proxy_url must be str or None, got {type(self.socks5_proxy_url)}"
            )

        if not (self._session is None or isinstance(self._session, ClientSession)):
            raise ClientValidationError(
                f"_session must be ClientSession or None, got {type(self._session)}"
            )

        if not (self._ws is None or isinstance(self._ws, ClientWebSocketResponse)):
            raise ClientValidationError(
                f"_ws must be ClientWebSocketResponse or None, got {type(self._ws)}"
            )

        if not isinstance(self._subscriptions, dict):
            raise ClientValidationError(
                f"_subscriptions must be dict, got {type(self._subscriptions)}"
            )
        for sub_id, sub_data in self._subscriptions.items():
            if not isinstance(sub_id, str):
                raise ClientValidationError(f"Subscription ID must be str, got {type(sub_id)}")
            if not isinstance(sub_data, dict):
                raise ClientValidationError(f"Subscription data must be dict, got {type(sub_data)}")
            if "filter" not in sub_data or "active" not in sub_data:
                raise ClientValidationError(
                    "Subscription data must contain 'filter' and 'active' keys"
                )
            if not (
                isinstance(sub_data["filter"], Filter)
                or type(sub_data["filter"]).__name__ == "Filter"
            ):
                raise ClientValidationError(
                    f"Subscription filter must be Filter, got {type(sub_data['filter'])}"
                )
            if not isinstance(sub_data["active"], bool):
                raise ClientValidationError(
                    f"Subscription 'active' must be bool, got {type(sub_data['active'])}"
                )
            if not sub_data["filter"].is_valid:
                raise ClientValidationError(f"Subscription filter is invalid: {sub_data['filter']}")

        if self.relay.network == "tor" and not self.socks5_proxy_url:
            raise ClientValidationError("socks5_proxy_url is required for Tor relays")

    @property
    def is_valid(self) -> bool:
        """
        Check if the Client configuration is valid.

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.validate()
            return True
        except ClientValidationError:
            return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Client":
        """
        Create Client from dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing client data
        Returns:
            Client: An instance of Client
        Raises:
            TypeError: If data is not a dictionary
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data)}")

        return cls(
            relay=Relay.from_dict(data["relay"]),
            timeout=data.get("timeout"),
            socks5_proxy_url=data.get("socks5_proxy_url"),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert Client to dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of Client with keys:
                - relay: Relay configuration dictionary
                - timeout: Connection timeout in seconds
                - socks5_proxy_url: SOCKS5 proxy URL for Tor relays

        Examples:
            >>> client = Client(relay, timeout=10)
            >>> client_dict = client.to_dict()
            >>> print(client_dict['timeout'])
            10
        """
        return {
            "relay": self.relay.to_dict(),
            "timeout": self.timeout,
            "socks5_proxy_url": self.socks5_proxy_url,
        }

    async def __aenter__(self) -> "Client":
        """
        Async context manager entry.

        Automatically connects to the relay when entering the context.
        This method is called when using the client in an async with statement.

        Returns:
            Client: Self for use in async with statement

        Examples:
            >>> async with Client(relay) as client:
            ...     # Client is automatically connected
            ...     await client.publish(event)
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: TracebackType) -> None:
        """
        Async context manager exit.

        Automatically disconnects from the relay when exiting the context.
        This method is called when leaving the async with statement.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Examples:
            >>> async with Client(relay) as client:
            ...     # Client is automatically connected
            ...     pass
            >>> # Client is automatically disconnected here
        """
        await self.disconnect()

    def connector(self) -> Union[TCPConnector, ProxyConnector]:
        """
        Create appropriate connector based on network type.

        Returns:
            Union[TCPConnector, ProxyConnector]: TCPConnector for clearnet or ProxyConnector for Tor

        Raises:
            ClientConnectionError: If SOCKS5 proxy URL required for Tor but not provided
        """
        if self.relay.network == "tor":
            if not self.socks5_proxy_url:
                raise ClientConnectionError("SOCKS5 proxy URL required for Tor relays")
            return ProxyConnector.from_url(self.socks5_proxy_url, force_close=True)
        else:
            return TCPConnector(force_close=True)

    def session(
        self, connector: Optional[Union[TCPConnector, ProxyConnector]] = None
    ) -> ClientSession:
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

        This method attempts to establish a WebSocket connection to the relay,
        trying both WSS (secure) and WS (insecure) protocols, preferring WSS.
        Creates HTTP session with appropriate connector (TCP or SOCKS5 proxy)
        based on relay network type.

        The method is idempotent - calling it when already connected will
        simply return without error.

        Raises:
            ClientConnectionError: If connection fails for any reason:
                - Network unreachable
                - Invalid relay URL
                - Timeout exceeded
                - SOCKS5 proxy connection failed (for Tor)

        Examples:
            >>> client = Client(relay)
            >>> await client.connect()
            >>> print(client.is_connected)
            True

            >>> # With timeout handling
            >>> try:
            ...     await client.connect()
            ... except ClientConnectionError as e:
            ...     print(f"Connection failed: {e}")
        """
        if self.is_connected:
            return  # Already connected

        try:
            connector = self.connector()
            self._session = self.session(connector=connector)
            relay_id = self.relay.url.removeprefix("wss://")

            # Try both WSS and WS protocols
            for schema in ["wss://", "ws://"]:
                try:
                    if self.timeout is not None:
                        ws_timeout = ClientWSTimeout(ws_close=self.timeout)
                        self._ws = await self._session.ws_connect(
                            schema + relay_id, timeout=ws_timeout
                        )
                    else:
                        self._ws = await self._session.ws_connect(schema + relay_id)
                    break
                except Exception as e:
                    logger.debug(f"Failed to connect via {schema}, trying next option: {e}")

            if not self._ws or self._ws.closed:
                raise Exception("Failed to establish WebSocket connection")

        except Exception as e:
            if self._session:
                await self._session.close()
                self._session = None
            raise ClientConnectionError(f"Failed to connect to {self.relay.url}: {e}") from e

    async def disconnect(self) -> None:
        """
        Close WebSocket connection and cleanup all resources.

        This method properly closes the WebSocket connection, HTTP session,
        and clears all active subscriptions. It's safe to call even if not
        connected.

        Resources cleaned up:
        - WebSocket connection closed gracefully
        - HTTP session terminated
        - All subscription state cleared
        - Internal buffers released

        Examples:
            >>> await client.connect()
            >>> # ... perform operations ...
            >>> await client.disconnect()
            >>> print(client.is_connected)
            False
        """
        if self._ws:
            await self._ws.close()
            self._ws = None

        if self._session:
            await self._session.close()
            self._session = None

        self._subscriptions.clear()

    async def send_message(self, message: list[Any]) -> None:
        """
        Send a message to the relay.

        Args:
            message (list[Any]): Message to send as a list (will be JSON encoded)

        Raises:
            ClientConnectionError: If not connected or send fails
            TypeError: If message is not a list
        """
        if not isinstance(message, list):
            raise TypeError(f"message must be a list, got {type(message)}")

        if not self._ws:
            raise ClientConnectionError("Not connected to relay")

        try:
            await self._ws.send_str(json.dumps(message))
        except Exception as e:
            raise ClientConnectionError(f"Failed to send message: {e}") from e

    async def subscribe(self, filter: Filter, subscription_id: Optional[str] = None) -> str:
        """
        Subscribe to events matching the given filter criteria.

        Sends a REQ message to the relay with the specified filter. The relay
        will send all stored events matching the filter, followed by real-time
        events as they arrive. A unique subscription ID is generated if not
        provided.

        Args:
            filter (Filter): Event filter criteria defining which events to receive.
                Can filter by kinds, authors, tags, time range, etc.
            subscription_id (Optional[str]): Custom subscription ID. If None, a
                UUID4 will be automatically generated. Useful for tracking
                multiple subscriptions.

        Returns:
            str: Subscription ID used to identify events and manage the subscription.
                Use this ID with listen_events() and unsubscribe().

        Raises:
            ClientConnectionError: If not connected or subscription fails.
            TypeError: If filter is not a Filter instance.
            ClientSubscriptionError: If subscription_id already exists and is active.

        Examples:
            Subscribe with auto-generated ID:

            >>> filter = Filter(kinds=[1], limit=10)
            >>> sub_id = await client.subscribe(filter)
            >>> print(f"Subscribed with ID: {sub_id}")

            Subscribe with custom ID:

            >>> filter = Filter(authors=["abc123..."])
            >>> sub_id = await client.subscribe(filter, "my-custom-sub")
            >>> async for msg in client.listen_events(sub_id):
            ...     process_event(msg)

            Multiple subscriptions:

            >>> # Subscribe to different event types
            >>> notes_sub = await client.subscribe(Filter(kinds=[1]))
            >>> reactions_sub = await client.subscribe(Filter(kinds=[7]))
        """
        if not (isinstance(filter, Filter) or type(filter).__name__ == "Filter"):
            raise TypeError(f"filter must be Filter, got {type(filter)}")

        if subscription_id is None:
            subscription_id = str(uuid.uuid4())

        # Check for duplicate active subscription
        if (
            subscription_id in self._subscriptions
            and self._subscriptions[subscription_id]["active"]
        ):
            raise ClientSubscriptionError(
                f"Subscription '{subscription_id}' already exists and is active. "
                "Use unsubscribe() first or choose a different subscription ID."
            )

        request = ["REQ", subscription_id, filter.subscription_filter]
        await self.send_message(request)

        self._subscriptions[subscription_id] = {"filter": filter, "active": True}

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> None:
        """
        Unsubscribe from events.

        Args:
            subscription_id (str): Subscription ID to close

        Raises:
            TypeError: If subscription_id is not a string
            ClientSubscriptionError: If subscription doesn't exist or is not active
        """
        if not isinstance(subscription_id, str):
            raise TypeError(f"subscription_id must be str, got {type(subscription_id)}")

        if subscription_id not in self._subscriptions:
            raise ClientSubscriptionError(
                f"Subscription '{subscription_id}' not found. "
                "Cannot unsubscribe from a non-existent subscription."
            )

        if not self._subscriptions[subscription_id]["active"]:
            raise ClientSubscriptionError(
                f"Subscription '{subscription_id}' is not active. It may have already been closed."
            )

        request = ["CLOSE", subscription_id]
        await self.send_message(request)
        self._subscriptions[subscription_id]["active"] = False

    async def publish(self, event: Event) -> None:
        """
        Publish an event to the relay.

        Sends an EVENT message to the relay with the provided event. Waits
        for an OK response from the relay to determine if the event was
        accepted. The event must be properly signed and validated before
        publishing. Returns on success or raises ClientPublicationError on failure.

        Args:
            event (Event): Event to publish. Must be a valid, signed Event
                instance. The event will be validated by the relay.

        Returns:
            None: Returns nothing on success. Raises ClientPublicationError on failure.

        Raises:
            ClientPublicationError: If the relay rejects the event or no OK response is received.
                Rejection can occur due to:
                - Invalid signature
                - Spam/rate limiting
                - Relay policy violations
                - Duplicate event
                - No response from relay
            ClientConnectionError: If not connected or communication fails.
            TypeError: If event is not an Event instance.

        Examples:
            Publish a text note:

            >>> from nostr_tools import generate_event
            >>> event_dict = generate_event(
            ...     private_key, public_key,
            ...     kind=1, tags=[], content="Hello Nostr!"
            ... )
            >>> event = Event.from_dict(event_dict)
            >>> try:
            ...     await client.publish(event)
            ...     print("Event published successfully!")
            ... except ClientPublicationError as e:
            ...     print(f"Event rejected: {e}")

            Publish with error handling:

            >>> try:
            ...     await client.publish(event)
            ...     print("Success!")
            ... except ClientPublicationError as e:
            ...     print(f"Publish failed: {e}")
            ... except ClientConnectionError as e:
            ...     print(f"Connection error: {e}")
        """
        if not (isinstance(event, Event) or type(event).__name__ == "Event"):
            raise TypeError(f"event must be Event, got {type(event)}")

        request = ["EVENT", event.to_dict()]
        await self.send_message(request)

        # Wait for OK response
        async for message in self.listen():
            if message[0] == "OK" and message[1] == event.id:
                accepted = bool(message[2])
                if not accepted:
                    # Relay rejected the event, get reason if available
                    reason = message[3] if len(message) > 3 else "No reason provided"
                    raise ClientPublicationError(f"Relay rejected event: {reason}")
                return  # Success!
            elif message[0] == "NOTICE":
                continue  # Ignore notices

        # No OK response received
        raise ClientPublicationError("No OK response received from relay")

    async def authenticate(self, event: Event) -> bool:
        """
        Authenticate with the relay using a NIP-42 event.

        Args:
            event (Event): Authentication event (must be kind 22242)

        Returns:
            bool: True if authentication successful, False otherwise

        Raises:
            ValueError: If event kind is not 22242
            TypeError: If event is not an Event instance
        """
        if not (isinstance(event, Event) or type(event).__name__ == "Event"):
            raise TypeError(f"event must be Event, got {type(event)}")

        if event.kind != 22242:
            raise ValueError("Event kind must be 22242 for authentication")

        request = ["AUTH", event.to_dict()]
        await self.send_message(request)

        # Wait for OK response
        async for message in self.listen():
            if message[0] == "OK" and message[1] == event.id:
                return bool(message[2])  # Explicit bool conversion
            elif message[0] == "NOTICE":
                continue

        return False

    async def listen(self) -> AsyncGenerator[list[Any], None]:
        """
        Listen for all messages from the relay.

        This async generator continuously listens for messages from the relay
        and yields them as they arrive. Messages are automatically parsed from
        JSON format. The generator continues until timeout, connection closure,
        or error.

        Message types from relay:
        - ["EVENT", subscription_id, event_dict]: New event matching subscription
        - ["EOSE", subscription_id]: End of stored events for subscription
        - ["OK", event_id, success, message]: Response to EVENT/AUTH message
        - ["NOTICE", message]: Relay notification or error message
        - ["CLOSED", subscription_id, message]: Subscription closed by relay

        Yields:
            list[Any]: Relay messages as parsed JSON lists. Format depends on
                message type (see above).

        Raises:
            ClientConnectionError: If not connected, connection fails, or
                encounters WebSocket errors.

        Examples:
            Listen to all relay messages:

            >>> async for message in client.listen():
            ...     msg_type = message[0]
            ...     if msg_type == "EVENT":
            ...         sub_id, event_dict = message[1], message[2]
            ...         event = Event.from_dict(event_dict)
            ...         print(f"Received event: {event.content}")
            ...     elif msg_type == "EOSE":
            ...         print(f"End of stored events for {message[1]}")
            ...     elif msg_type == "NOTICE":
            ...         print(f"Relay notice: {message[1]}")

            With timeout handling:

            >>> try:
            ...     async for message in client.listen():
            ...         process_message(message)
            ... except asyncio.TimeoutError:
            ...     print("No messages received within timeout")
        """
        if not self._ws:
            raise ClientConnectionError("Not connected to relay")

        try:
            while True:
                if self.timeout is not None:
                    msg = await asyncio.wait_for(self._ws.receive(), timeout=self.timeout)
                else:
                    msg = await self._ws.receive()

                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        yield data
                    except json.JSONDecodeError:
                        continue
                elif msg.type == WSMsgType.ERROR:
                    raise ClientConnectionError(f"WebSocket error: {msg.data}")
                elif msg.type == WSMsgType.CLOSED:
                    break
                else:
                    raise ClientConnectionError(f"Unexpected message type: {msg.type}")

        except asyncio.TimeoutError:
            pass
        except Exception as e:
            raise ClientConnectionError(f"Error listening to relay: {e}") from e

    async def listen_events(
        self,
        subscription_id: str,
    ) -> AsyncGenerator[list[Any], None]:
        """
        Listen for events from a specific subscription.

        This method filters messages to only yield events from the
        specified subscription until the subscription ends.

        Args:
            subscription_id (str): Subscription to listen to

        Yields:
            list[Any]: Events received from the subscription

        Raises:
            TypeError: If subscription_id is not a string
        """
        if not isinstance(subscription_id, str):
            raise TypeError(f"subscription_id must be str, got {type(subscription_id)}")

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
        Check if client is currently connected to the relay.

        This property checks if the WebSocket connection is active and not closed.

        Returns:
            bool: True if connected and WebSocket is open, False otherwise.

        Examples:
            >>> if client.is_connected:
            ...     await client.publish(event)
            ... else:
            ...     await client.connect()

            >>> async with client:
            ...     assert client.is_connected  # True inside context
            >>> assert not client.is_connected  # False after context exit
        """
        return self._ws is not None and not self._ws.closed

    @property
    def active_subscriptions(self) -> list[str]:
        """
        Get list of currently active subscription IDs.

        Returns list of subscription IDs that are active (not closed/unsubscribed).
        Useful for tracking and managing multiple concurrent subscriptions.

        Returns:
            list[str]: List of subscription IDs that are currently active.
                Empty list if no active subscriptions.

        Examples:
            >>> sub1 = await client.subscribe(Filter(kinds=[1]))
            >>> sub2 = await client.subscribe(Filter(kinds=[7]))
            >>> print(client.active_subscriptions)
            ['sub_id_1', 'sub_id_2']

            >>> await client.unsubscribe(sub1)
            >>> print(client.active_subscriptions)
            ['sub_id_2']

            >>> # Close all active subscriptions
            >>> for sub_id in client.active_subscriptions:
            ...     await client.unsubscribe(sub_id)
        """
        return [sub_id for sub_id, sub_data in self._subscriptions.items() if sub_data["active"]]
