Welcome to nostr-tools documentation!
=====================================

.. image:: https://img.shields.io/pypi/v/nostr-tools.svg
   :target: https://pypi.org/project/nostr-tools/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/nostr-tools.svg
   :target: https://pypi.org/project/nostr-tools/
   :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/bigbrotr/nostr-tools/blob/main/LICENSE
   :alt: License

A comprehensive Python library for interacting with the Nostr protocol. This library provides high-level and low-level APIs for connecting to Nostr relays, publishing and subscribing to events, and managing cryptographic operations.

Features
--------

- **Complete Nostr Protocol Support**: Full implementation of NIP-01, NIP-11, NIP-13, and partial NIP-42
- **Async/Await API**: Modern Python async support for high-performance applications
- **Advanced Relay Management**: Connect to relays with comprehensive metadata analysis
- **Event Handling**: Create, sign, verify, and filter Nostr events with full validation
- **Cryptographic Operations**: Built-in key generation, Schnorr signatures, and proof-of-work mining
- **Tor Support**: Connect to .onion relays through SOCKS5 proxies
- **Type Safety**: Complete type hints and runtime validation
- **Performance Optimized**: Efficient cryptographic operations and connection management

Quick Start
-----------

.. code-block:: python

   import asyncio
   from nostr_tools import Client, Relay, generate_keypair, generate_event, Event

   async def main():
       # Generate a new key pair
       private_key, public_key = generate_keypair()

       # Create a relay connection
       relay = Relay("wss://relay.damus.io")
       client = Client(relay)

       async with client:
           # Create and publish an event
           event_data = generate_event(
               private_key, public_key, 1, [], "Hello Nostr!"
           )
           event = Event.from_dict(event_data)
           success = await client.publish(event)
           print(f"Published: {success}")

   asyncio.run(main())

Installation
------------

.. code-block:: bash

   pip install nostr-tools

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   tutorials/index
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/core
   api/actions
   api/utils
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   security
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
