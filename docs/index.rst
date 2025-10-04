============================
nostr-tools Documentation
============================

.. include:: ../README.md
   :parser: myst_parser.sphinx_


API Reference
-------------

Core
~~~~

.. autosummary::
   :toctree: _autosummary
   :recursive:

   nostr_tools.Event
   nostr_tools.Client
   nostr_tools.Filter
   nostr_tools.Relay
   nostr_tools.RelayMetadata

Utils
~~~~~

.. autosummary::
   :toctree: _autosummary
   :recursive:

   nostr_tools.generate_keypair
   nostr_tools.generate_event
   nostr_tools.verify_sig
   nostr_tools.to_bech32
   nostr_tools.to_hex
   nostr_tools.validate_keypair
   nostr_tools.calc_event_id
   nostr_tools.sig_event_id
   nostr_tools.sanitize
   nostr_tools.find_ws_urls

Actions
~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :recursive:

   nostr_tools.fetch_events
   nostr_tools.stream_events
   nostr_tools.fetch_nip11
   nostr_tools.fetch_nip66
   nostr_tools.fetch_relay_metadata
   nostr_tools.check_connectivity
   nostr_tools.check_readability
   nostr_tools.check_writability

Exceptions
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :recursive:

   nostr_tools.NostrToolsError
   nostr_tools.EventValidationError
   nostr_tools.FilterValidationError
   nostr_tools.RelayValidationError
   nostr_tools.KeyValidationError
   nostr_tools.EncodingError
   nostr_tools.RelayConnectionError
   nostr_tools.PublishError
   nostr_tools.SubscriptionError
