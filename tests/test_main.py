"""Tests for the main module."""

from unittest.mock import patch

from reff_extractor_racer_team.main import main


def test_main_runs_without_error():
    """Test that main() executes successfully."""
    # Mock get_connected_serials to return empty set (no devices connected).
    # This allows the test to pass without requiring ADB or connected devices.
    with patch(
        "reff_extractor_racer_team.collector.get_connected_serials",
        return_value=set(),
    ):
        main()


def test_main_can_be_imported():
    """Test that main function can be imported from the main module."""
    from reff_extractor_racer_team.main import main as imported_main

    assert callable(imported_main)
