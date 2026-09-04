"""Shared ADB command helpers."""

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence


@dataclass
class AndroidDevice:
    """Represents an Android device connected to the computer."""

    name: str
    serial: str
    remote_log_path: str
    file_prefix: str
    apk_file_name: str


today_str = datetime.now().strftime("%d-%m-%Y")
home = Path.home()
onedrive_desktop = home / "OneDrive" / "Desktop"
standard_desktop = home / "Desktop"

DESKTOP_PATH = onedrive_desktop if onedrive_desktop.exists() else standard_desktop
LOCAL_DUMP_DIR = str(DESKTOP_PATH / f"Reff_{today_str}")
VIDEO_REMOTE_PATH = "/sdcard/Eyesatop-Records/Screen-Videos"

DEVICES_REGISTRY: list[AndroidDevice] = [
    AndroidDevice(
        name="Racer Controller",
        serial="4LFCN380071TMZ",
        remote_log_path="/sdcard/Records",
        file_prefix="RACER",
        apk_file_name="",
    ),
    AndroidDevice(
        name="Koren's Tablet",
        serial="R52Y901B9AP",
        remote_log_path="/sdcard/Records",
        file_prefix="TABLET",
        apk_file_name="",
    ),
    AndroidDevice(
        name="RC PAD Home",
        serial="f7b2909c",
        remote_log_path="/sdcard/Records",
        file_prefix="ISR",
        apk_file_name="",
    ),
]


def run_adb_command(
    command: Sequence[str], *, check: bool = False
) -> subprocess.CompletedProcess[str]:
    """Run an ADB command and return its completed process result."""

    return subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        check=check,
    )


def get_connected_serials() -> set[str]:
    """Return the serial numbers of all connected Android devices."""

    try:
        result = run_adb_command(["adb", "devices"], check=True)
        connected_serials = set()

        for line in result.stdout.splitlines():
            match = re.match(r"^\s*(\S+)\s+device\s*$", line)

            if match:
                connected_serials.add(match.group(1))

        if not connected_serials:
            print("[!] No connected devices found.")

        return connected_serials

    except Exception as error:
        print(f"[!] Failed to detect connected devices: {error}")
        return set()


def get_conneccted_android_devices() -> list[AndroidDevice]:
    """Return a list of connected AndroidDevice instances based on the registry."""

    connected_serials = get_connected_serials()
    connected_devices = [
        device for device in DEVICES_REGISTRY if device.serial in connected_serials
    ]

    return connected_devices


__all__ = [
    "AndroidDevice",
    "DEVICES_REGISTRY",
    "LOCAL_DUMP_DIR",
    "VIDEO_REMOTE_PATH",
    "get_connected_serials",
    "run_adb_command",
]
