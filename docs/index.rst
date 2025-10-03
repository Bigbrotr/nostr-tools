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

API Documentation
-----------------

Core
~~~~~

.. autosummary::
   :toctree: _autosummary
   :caption: Core

   nostr_tools.Client
   nostr_tools.Event
   nostr_tools.Filter
   nostr_tools.Relay
   nostr_tools.RelayMetadata

Utilities
~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :caption: Utilities

   nostr_tools.generate_keypair
   nostr_tools.generate_event
   nostr_tools.calc_event_id
   nostr_tools.verify_sig
   nostr_tools.to_bech32
   nostr_tools.to_hex

Actions
~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :caption: High-level Actions

   nostr_tools.fetch_events
   nostr_tools.stream_events
   nostr_tools.check_connectivity
   nostr_tools.fetch_nip11

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
