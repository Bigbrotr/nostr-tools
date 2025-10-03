Nostr-Tools Documentation
==========================

.. image:: https://img.shields.io/pypi/v/nostr-tools.svg
   :target: https://pypi.org/project/nostr-tools/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/nostr-tools.svg
   :target: https://pypi.org/project/nostr-tools/
   :alt: Python Versions

.. image:: https://img.shields.io/github/license/bigbrotr/nostr-tools.svg
   :target: https://github.com/bigbrotr/nostr-tools/blob/main/LICENSE
   :alt: License

.. image:: https://github.com/bigbrotr/nostr-tools/workflows/CI/badge.svg
   :target: https://github.com/bigbrotr/nostr-tools/actions
   :alt: CI Status

.. image:: https://img.shields.io/codecov/c/github/bigbrotr/nostr-tools.svg
   :target: https://codecov.io/gh/bigbrotr/nostr-tools
   :alt: Coverage

.. image:: https://static.pepy.tech/badge/nostr-tools
   :target: https://pepy.tech/project/nostr-tools
   :alt: Downloads

A comprehensive Python library for Nostr protocol interactions.

Features
--------

✨ **Complete Nostr Implementation**
   Full support for the Nostr protocol specification with modern Python async/await patterns.

🔒 **Robust Cryptography**
   Built-in support for secp256k1 signatures, key generation, and Bech32 encoding.

🌐 **WebSocket Relay Management**
   Efficient WebSocket client with automatic connection handling and relay URL validation.

🔄 **Async/Await Support**
   Fully asynchronous API designed for high-performance applications.

📘 **Complete Type Hints**
   Full type annotation coverage for excellent IDE support and development experience.

🧪 **Comprehensive Testing**
   Extensive test suite with unit tests and integration tests covering 80%+ of the codebase.

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install nostr-tools

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from nostr_tools import Client, generate_keypair, Event

   async def main():
       # Generate a new keypair
       private_key, public_key = generate_keypair()

       # Create a client
       client = Client()

       # Connect to a relay
       await client.connect("wss://relay.damus.io")

       # Create and publish an event
       event = Event(
           kind=1,
           content="Hello Nostr!",
           public_key=public_key
       )

       # Sign and publish the event
       signed_event = event.sign(private_key)
       await client.publish(signed_event)

       # Subscribe to events
       async for event in client.subscribe({"kinds": [1], "limit": 10}):
           print(f"Received: {event.content}")

       await client.disconnect()

   if __name__ == "__main__":
       asyncio.run(main())

API Reference
-------------

Complete API documentation organized by module. Every class, method, function, and exception is fully documented.

Core Module
~~~~~~~~~~~

All core classes for Nostr protocol interactions with complete method documentation.

.. autosummary::
   :toctree: _autosummary
   :template: class.rst

   nostr_tools.Client
   nostr_tools.Event
   nostr_tools.Filter
   nostr_tools.Relay
   nostr_tools.RelayMetadata

Utils Module
~~~~~~~~~~~~

All utility functions for cryptography, encoding, and data processing.

.. autosummary::
   :toctree: _autosummary

   nostr_tools.calc_event_id
   nostr_tools.verify_sig
   nostr_tools.sig_event_id
   nostr_tools.generate_keypair
   nostr_tools.validate_keypair
   nostr_tools.generate_event
   nostr_tools.to_bech32
   nostr_tools.to_hex
   nostr_tools.find_ws_urls
   nostr_tools.sanitize

Actions Module
~~~~~~~~~~~~~~

All high-level action functions for relay operations.

.. autosummary::
   :toctree: _autosummary

   nostr_tools.fetch_events
   nostr_tools.stream_events
   nostr_tools.fetch_nip11
   nostr_tools.fetch_nip66
   nostr_tools.fetch_relay_metadata
   nostr_tools.check_connectivity
   nostr_tools.check_readability
   nostr_tools.check_writability

Exceptions Module
~~~~~~~~~~~~~~~~~

All exception classes for error handling.

.. autosummary::
   :toctree: _autosummary
   :template: class.rst

   nostr_tools.NostrToolsError
   nostr_tools.RelayConnectionError
   nostr_tools.EventValidationError
   nostr_tools.KeyValidationError
   nostr_tools.FilterValidationError
   nostr_tools.RelayValidationError
   nostr_tools.SubscriptionError
   nostr_tools.PublishError
   nostr_tools.EncodingError

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
