"""
Package-level tests for nostr-tools.

This module tests package-level functionality including:
- Package imports and exports
- Version information
- Lazy loading
- Public API availability
- Package metadata
"""

import sys

import pytest

# ============================================================================
# Package Import Tests
# ============================================================================


@pytest.mark.unit
class TestPackageImports:
    """Test package imports."""

    def test_import_nostr_tools(self) -> None:
        """Test that nostr_tools can be imported."""
        import nostr_tools

        assert nostr_tools is not None

    def test_import_core_modules(self) -> None:
        """Test importing core modules."""
        from nostr_tools import Client
        from nostr_tools import Event
        from nostr_tools import Filter
        from nostr_tools import Relay
        from nostr_tools import RelayMetadata

        assert Client is not None
        assert Event is not None
        assert Filter is not None
        assert Relay is not None
        assert RelayMetadata is not None

    def test_import_utility_functions(self) -> None:
        """Test importing utility functions."""
        from nostr_tools import calc_event_id
        from nostr_tools import generate_event
        from nostr_tools import generate_keypair
        from nostr_tools import to_bech32
        from nostr_tools import to_hex
        from nostr_tools import verify_sig

        assert calc_event_id is not None
        assert generate_event is not None
        assert generate_keypair is not None
        assert to_bech32 is not None
        assert to_hex is not None
        assert verify_sig is not None

    def test_import_action_functions(self) -> None:
        """Test importing action functions."""
        from nostr_tools import check_connectivity
        from nostr_tools import fetch_events
        from nostr_tools import fetch_nip11

        assert check_connectivity is not None
        assert fetch_events is not None
        assert fetch_nip11 is not None

    def test_import_exceptions(self) -> None:
        """Test importing exceptions."""
        from nostr_tools import ClientConnectionError

        assert ClientConnectionError is not None
        assert issubclass(ClientConnectionError, Exception)


# ============================================================================
# Package Metadata Tests
# ============================================================================


@pytest.mark.unit
class TestPackageMetadata:
    """Test package metadata."""

    def test_package_has_version(self) -> None:
        """Test that package has __version__."""
        import nostr_tools

        assert hasattr(nostr_tools, "__version__")
        assert isinstance(nostr_tools.__version__, str)
        assert len(nostr_tools.__version__) > 0

    def test_package_has_author(self) -> None:
        """Test that package has __author__."""
        import nostr_tools

        assert hasattr(nostr_tools, "__author__")
        assert isinstance(nostr_tools.__author__, str)

    def test_package_has_email(self) -> None:
        """Test that package has __email__."""
        import nostr_tools

        assert hasattr(nostr_tools, "__email__")
        assert isinstance(nostr_tools.__email__, str)

    def test_get_info_function(self) -> None:
        """Test get_info() function."""
        import nostr_tools

        info = nostr_tools.get_info()
        assert isinstance(info, dict)
        assert "name" in info
        assert "version" in info
        assert "author" in info
        assert "email" in info
        assert "description" in info


# ============================================================================
# Public API Tests
# ============================================================================


@pytest.mark.unit
class TestPublicAPI:
    """Test public API availability."""

    def test_all_exports_are_available(self) -> None:
        """Test that all __all__ exports are available."""
        import nostr_tools

        for name in nostr_tools.__all__:
            assert hasattr(
                nostr_tools, name), f"{name} not available in package"

    def test_dir_returns_all_exports(self) -> None:
        """Test that dir() returns all exports."""
        import nostr_tools

        dir_result = dir(nostr_tools)
        for name in nostr_tools.__all__:
            assert name in dir_result, f"{name} not in dir() output"

    def test_exported_symbols_are_not_none(self) -> None:
        """Test that exported symbols are not None."""
        import nostr_tools

        for name in nostr_tools.__all__:
            attr = getattr(nostr_tools, name)
            assert attr is not None, f"{name} is None"


# ============================================================================
# Lazy Loading Tests
# ============================================================================


@pytest.mark.unit
class TestLazyLoading:
    """Test lazy loading functionality."""

    def test_lazy_loading_works(self) -> None:
        """Test that lazy loading imports work."""
        # Force reload to test lazy loading
        if "nostr_tools" in sys.modules:
            # Store BUILDING_DOCS state

            # Unload the module
            modules_to_remove = [
                mod for mod in sys.modules if mod.startswith("nostr_tools")]
            for mod in modules_to_remove:
                del sys.modules[mod]

            # Reimport
            import nostr_tools as nt

            # Should still be able to access exports
            assert nt.Event is not None
            assert nt.generate_keypair is not None

    def test_lazy_imports_are_callable(self) -> None:
        """Test that lazy-loaded functions are callable."""
        from nostr_tools import generate_keypair

        # Should be callable
        private_key, public_key = generate_keypair()
        assert len(private_key) == 64
        assert len(public_key) == 64


# ============================================================================
# Module Structure Tests
# ============================================================================


@pytest.mark.unit
class TestModuleStructure:
    """Test module structure."""

    def test_core_module_exists(self) -> None:
        """Test that core module exists."""
        from nostr_tools import core

        assert core is not None

    def test_utils_module_exists(self) -> None:
        """Test that utils module exists."""
        from nostr_tools import utils

        assert utils is not None

    def test_actions_module_exists(self) -> None:
        """Test that actions module exists."""
        from nostr_tools import actions

        assert actions is not None

    def test_exceptions_module_exists(self) -> None:
        """Test that exceptions module exists."""
        from nostr_tools import exceptions

        assert exceptions is not None


# ============================================================================
# Submodule Import Tests
# ============================================================================


@pytest.mark.unit
class TestSubmoduleImports:
    """Test importing from submodules."""

    def test_import_from_core_event(self) -> None:
        """Test importing from core.event."""
        from nostr_tools.core.event import Event

        assert Event is not None

    def test_import_from_core_filter(self) -> None:
        """Test importing from core.filter."""
        from nostr_tools.core.filter import Filter

        assert Filter is not None

    def test_import_from_core_relay(self) -> None:
        """Test importing from core.relay."""
        from nostr_tools.core.relay import Relay

        assert Relay is not None

    def test_import_from_core_client(self) -> None:
        """Test importing from core.client."""
        from nostr_tools.core.client import Client

        assert Client is not None

    def test_import_from_utils(self) -> None:
        """Test importing from utils."""
        from nostr_tools.utils.utils import generate_keypair

        assert generate_keypair is not None

    def test_import_from_actions(self) -> None:
        """Test importing from actions."""
        from nostr_tools.actions.actions import fetch_events

        assert fetch_events is not None

    def test_import_from_exceptions(self) -> None:
        """Test importing from exceptions."""
        from nostr_tools.exceptions.errors import ClientConnectionError

        assert ClientConnectionError is not None


# ============================================================================
# Constants Tests
# ============================================================================


@pytest.mark.unit
class TestConstants:
    """Test package constants."""

    def test_tlds_constant(self) -> None:
        """Test TLDS constant."""
        from nostr_tools import TLDS

        assert isinstance(TLDS, list)
        assert len(TLDS) > 0
        assert all(isinstance(tld, str) for tld in TLDS)

    def test_uri_regex_constant(self) -> None:
        """Test URI_GENERIC_REGEX constant."""
        from nostr_tools import URI_GENERIC_REGEX

        assert isinstance(URI_GENERIC_REGEX, str)
        assert len(URI_GENERIC_REGEX) > 0


# ============================================================================
# Package Component Integration Tests
# ============================================================================


@pytest.mark.unit
class TestPackageIntegration:
    """Test integration between package components."""

    def test_create_event_flow(self) -> None:
        """Test complete event creation flow using package imports."""
        from nostr_tools import Event
        from nostr_tools import generate_event
        from nostr_tools import generate_keypair

        # Generate keypair
        private_key, public_key = generate_keypair()

        # Create event
        event_dict = generate_event(private_key, public_key, 1, [], "Test")

        # Create Event object
        event = Event.from_dict(event_dict)

        # Verify event
        assert event.is_valid

    def test_filter_subscription_flow(self) -> None:
        """Test filter creation flow."""
        from nostr_tools import Filter

        # Create filter
        filter = Filter(kinds=[1], limit=10)

        # Get subscription filter
        sub_filter = filter.subscription_filter

        assert "kinds" in sub_filter
        assert "limit" in sub_filter

    def test_relay_client_flow(self) -> None:
        """Test relay and client creation flow."""
        from nostr_tools import Client
        from nostr_tools import Relay

        # Create relay
        relay = Relay(url="wss://relay.damus.io")

        # Create client
        client = Client(relay=relay, timeout=10)

        assert client.is_valid
        assert client.relay.url == "wss://relay.damus.io"


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.unit
class TestPackageErrorHandling:
    """Test package error handling."""

    def test_import_nonexistent_raises_error(self) -> None:
        """Test that importing nonexistent symbol raises error."""
        with pytest.raises((AttributeError, ImportError)):
            from nostr_tools import NonExistentSymbol  # type: ignore  # noqa: F401

    def test_client_connection_error_is_available(self) -> None:
        """Test that ClientConnectionError is accessible."""
        from nostr_tools import ClientConnectionError

        error = ClientConnectionError("test")
        assert isinstance(error, Exception)
