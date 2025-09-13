nostr-tools Documentation
=========================

.. image:: https://img.shields.io/pypi/v/nostr-tools.svg
   :target: https://pypi.org/project/nostr-tools/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/nostr-tools.svg
   :target: https://pypi.org/project/nostr-tools/
   :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/bigbrotr/nostr-tools/blob/main/LICENSE
   :alt: License

A comprehensive Python library for interacting with the Nostr protocol.

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

API Reference
=============

.. currentmodule:: nostr_tools

Core Classes
------------

.. autosummary::
   :toctree: _autosummary

   Event
   Relay
   Client
   Filter
   RelayMetadata

High-Level Functions
--------------------

.. autosummary::
   :toctree: _autosummary

   fetch_events
   stream_events
   compute_relay_metadata
   check_connectivity
   check_readability
   check_writability
   fetch_nip11
   fetch_connection

Cryptographic Functions
-----------------------

.. autosummary::
   :toctree: _autosummary

   generate_keypair
   validate_keypair
   generate_event
   calc_event_id
   sig_event_id
   verify_sig

Utility Functions
-----------------

.. autosummary::
   :toctree: _autosummary

   to_bech32
   to_hex
   find_websocket_relay_urls
   sanitize
   parse_nip11_response
   parse_connection_response

Exceptions
----------

.. autosummary::
   :toctree: _autosummary

   RelayConnectionError

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
