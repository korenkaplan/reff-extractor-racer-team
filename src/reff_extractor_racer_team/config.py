from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass
class AndroidDevice:
    """Represents an android device connected to the computer"""

    name: str
    serial: str
    remote_log_path: str
    file_prefix: str


today_str = datetime.now().strftime("%d-%m-%Y")

# זיהוי נתיב ה-Desktop (מקומי או OneDrive)
home = Path.home()
onedrive_desktop = home / "OneDrive" / "Desktop"
standard_desktop = home / "Desktop"

DESKTOP_PATH = onedrive_desktop if onedrive_desktop.exists() else standard_desktop

# התיקייה הסופית שתיווצר בשולחן העבודה
LOCAL_DUMP_DIR = str(DESKTOP_PATH / f"Reff_{today_str}")

DEVICES_REGISTRY: List[AndroidDevice] = [
    AndroidDevice(
        name="Racer Controller",
        serial="4LFCN380071TMZ",
        remote_log_path="/sdcard/Records",
        file_prefix="RACER",
    ),
    AndroidDevice(
        name="Koren's Tablet",
        serial="R52Y901B9AP",
        remote_log_path="/sdcard/Records",
        file_prefix="TABLET",
    ),
    AndroidDevice(
            name="RC PAD Home",
            serial="f7b2909c",
            remote_log_path="/sdcard/Records",
            file_prefix="ISR",
        ),
]
