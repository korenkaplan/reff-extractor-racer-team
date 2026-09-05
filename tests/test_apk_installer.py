"""Tests for the APK installer flow."""

import os
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from rich.console import Console

from racer_team_toolkit.apk_installer.functions import (
    build_installation_plan,
    find_matching_apk,
    get_folders_in_downloads,
    run_installation,
)
from racer_team_toolkit.config import AndroidDevice


def make_device(name: str = "Tablet") -> AndroidDevice:
    """Build a test device with a predictable APK pattern."""

    return AndroidDevice(
        name=name,
        serial="TEST123",
        remote_log_path="/sdcard/Records",
        file_prefix="TEST",
        apk_name_pattern="app-debug-*.apk",
        package_name="com.example.app",
    )


def test_get_folders_in_downloads_returns_only_apk_folders(tmp_path: Path) -> None:
    """Only Downloads directories containing APK files are returned."""

    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    (downloads / "root-app.apk").write_bytes(b"apk")
    matching_folder = downloads / "matching"
    matching_folder.mkdir()
    (matching_folder / "app.apk").write_bytes(b"apk")
    empty_folder = downloads / "empty"
    empty_folder.mkdir()
    (downloads / "readme.txt").write_text("not an APK")

    with patch("pathlib.Path.home", return_value=tmp_path):
        folders = get_folders_in_downloads()

    assert folders == [downloads, matching_folder]


def test_find_matching_apk_returns_newest_file(tmp_path: Path) -> None:
    """The newest matching APK is selected for installation."""

    older = tmp_path / "app-debug-1.apk"
    newest = tmp_path / "app-debug-2.apk"
    older.write_bytes(b"old")
    newest.write_bytes(b"new")
    os.utime(older, (1, 1))
    os.utime(newest, (2, 2))

    selected = find_matching_apk(tmp_path, make_device())

    assert selected == newest


def test_build_installation_plan_keeps_missing_devices() -> None:
    """Devices without an APK remain in the plan with no path."""

    device = make_device()
    plan = build_installation_plan(Path("/does/not/exist"), [device])

    assert len(plan) == 1
    assert plan[0].device is device
    assert plan[0].apk_path is None


def test_run_installation_stops_after_uninstall_failure(tmp_path: Path) -> None:
    """An uninstall failure prevents install and permission operations."""

    apk_path = tmp_path / "app-debug-1.apk"
    apk_path.write_bytes(b"apk")
    plan = build_installation_plan(tmp_path, [make_device()])[0]
    fake_console = Console(record=True)

    with patch(
        "racer_team_toolkit.apk_installer.functions.run_adb_command",
        return_value=CompletedProcess([], 1, "", "uninstall failed"),
    ) as run_command:
        result = run_installation(plan, fake_console)

    assert result.status == "failed"
    assert "uninstall failed" in result.message
    assert "ADB exit code 1" in result.message
    assert run_command.call_count == 1
    assert run_command.call_args.args[0][3:5] == ["shell", "pm"]
    assert run_command.call_args.args[0][5] == "uninstall"


def test_uninstall_accepts_missing_application(tmp_path: Path) -> None:
    """A package that is not installed should not block installation."""

    apk_path = tmp_path / "app-debug-1.apk"
    apk_path.write_bytes(b"apk")
    plan = build_installation_plan(tmp_path, [make_device()])[0]
    fake_console = Console(record=True)

    with patch(
        "racer_team_toolkit.apk_installer.functions.run_adb_command",
        return_value=CompletedProcess([], 1, "Failure [not installed]", ""),
    ):
        result = run_installation(plan, fake_console)

    assert result.status == "failed"
    assert "ADB exit code 1" in result.message
    assert "Failure [not installed]" in result.message
