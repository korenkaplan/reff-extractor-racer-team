"""Tests for the main module."""

from reff_extractor_racer_team import main


def test_main_runs_without_error(capsys):
    """Test that main() executes successfully."""
    main()
    captured = capsys.readouterr()
    assert "Hello from reff-extractor-racer-team!" in captured.out
