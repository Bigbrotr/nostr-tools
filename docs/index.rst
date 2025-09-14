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

.. image:: https://github.com/bigbrotr/nostr-tools/workflows/Test/badge.svg
   :target: https://github.com/bigbrotr/nostr-tools/actions
   :alt: Test Status

A comprehensive Python library for Nostr protocol interactions.

Features
--------

✨ **Complete Nostr Implementation**
   Full support for the Nostr protocol specification with modern Python async/await patterns.

🔒 **Robust Cryptography**
   Built-in support for secp256k1 signatures, key generation, and Bech32 encoding.

🌐 **WebSocket Relay Management**
   Efficient WebSocket client with connection pooling, automatic reconnection, and relay discovery.

🔄 **Async/Await Support**
   Fully asynchronous API designed for high-performance applications.

📘 **Complete Type Hints**
   Full type annotation coverage for excellent IDE support and development experience.

🧪 **Comprehensive Testing**
   Extensive test suite with unit tests, integration tests, and security checks.

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

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   examples
   best_practices

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/event
   api/relay
   api/utils
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   testing
   changelog

API Documentation
-----------------

Core Classes
~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :caption: Core Classes

   nostr_tools.Client
   nostr_tools.Event
   nostr_tools.Relay
   nostr_tools.Filter
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
