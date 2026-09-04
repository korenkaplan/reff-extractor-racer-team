"""Tests for the application."""

import os
from pathlib import Path
from unittest.mock import patch

from reff_extractor_racer_team.collector import attach_videos_to_flight
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


def test_attach_videos_to_flight_moves_videos_within_time_limit(tmp_path: Path):
    """Videos close to a flight log are moved into that flight folder."""
    flight_dir = tmp_path / "Flight_01"
    flight_dir.mkdir()
    video_path = tmp_path / "VIDEO_TABLET_recording.mp4"
    video_path.write_bytes(b"video")
    os.utime(video_path, (1_060, 1_060))

    flight_files = [{"mtime": 1_000}]
    videos = [{"filename": video_path.name, "path": str(video_path), "mtime": 1_060}]

    assert attach_videos_to_flight(str(flight_dir), flight_files, videos) == 1
    assert (flight_dir / video_path.name).exists()
    assert not video_path.exists()
