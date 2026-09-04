"""Shared ADB command helpers."""

import re
import subprocess
from typing import Sequence


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


__all__ = ["get_connected_serials", "run_adb_command"]
