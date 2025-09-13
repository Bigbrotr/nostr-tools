API Reference
=============

This section contains the complete API documentation for nostr-tools, automatically generated from docstrings.

.. toctree::
   :maxdepth: 2

   core
   actions
   utils
   exceptions

Overview
--------

The nostr-tools library is organized into several key modules:

* :doc:`core` - Core Nostr protocol components (Event, Relay, Client, Filter)
* :doc:`actions` - High-level action functions for common operations
* :doc:`utils` - Utility functions for cryptography, encoding, and data processing
* :doc:`exceptions` - Custom exception classes

Quick Reference
---------------

Core Classes
~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   nostr_tools.Event
   nostr_tools.Relay
   nostr_tools.Client
   nostr_tools.Filter
   nostr_tools.RelayMetadata

High-Level Functions
~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   nostr_tools.fetch_events
   nostr_tools.stream_events
   nostr_tools.compute_relay_metadata
   nostr_tools.generate_keypair
   nostr_tools.generate_event
