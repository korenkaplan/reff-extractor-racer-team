"""Central configuration for the Racer Team Toolkit."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class AndroidDevice:
    """Represents an Android device connected to the computer."""

    name: str
    serial: str
    remote_log_path: str
    file_prefix: str
    apk_file_name: str


# Shared ADB and device settings.
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

# REFF extraction settings.
MAX_FLIGHT_TIME_DIFF = 120
MAX_VIDEO_TIME_DIFF = 240
SUPPORTED_DEVICE_TYPES = ("RACER", "TABLET", "ISR")

# Main menu settings.
TOOL_MENU_CHOICES = [
    "REFF & Video Extractor",
    "APK Installer",
    "JAR Management",
    "Exit",
]
APK_INSTALLER_HEADER = "Select a folder to install APKs from:"
JAR_MANAGEMENT_HEADER = "Select a JAR management option:"
JAR_MANAGEMENT_CHOICES = ["Upload JAR", "Restart JAR", "Return to Main Menu"]


__all__ = [
    "APK_INSTALLER_HEADER",
    "AndroidDevice",
    "DEVICES_REGISTRY",
    "DESKTOP_PATH",
    "JAR_MANAGEMENT_CHOICES",
    "JAR_MANAGEMENT_HEADER",
    "LOCAL_DUMP_DIR",
    "MAX_FLIGHT_TIME_DIFF",
    "MAX_VIDEO_TIME_DIFF",
    "SUPPORTED_DEVICE_TYPES",
    "TOOL_MENU_CHOICES",
    "VIDEO_REMOTE_PATH",
]
