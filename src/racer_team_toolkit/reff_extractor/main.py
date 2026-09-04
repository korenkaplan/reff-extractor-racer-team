"""Main entry point for the Reff Extractor application."""

import os

from racer_team_toolkit.adb import DEVICES_REGISTRY, LOCAL_DUMP_DIR, get_connected_serials

from .collector import (
    group_files_into_flights,
    process_device,
)


def main() -> None:
    print("==================================================")
    print("       Starting Reff Extraction                   ")
    print("==================================================")

    print(f"[i] Saving files to path:\n    {os.path.abspath(LOCAL_DUMP_DIR)}\n")

    os.makedirs(LOCAL_DUMP_DIR, exist_ok=True)

    connected_serials = get_connected_serials()

    if not connected_serials:
        print("[-] No connected ADB devices found.")
        return

    print(f"[+] Total devices connected: {len(connected_serials)}")

    processed_any = False

    for device in DEVICES_REGISTRY:
        if device.serial in connected_serials:
            process_device(device)
            processed_any = True

        else:
            print(f"[i] {device.name} (Serial: {device.serial}) - Not connected, skipping.")

    # --------------------------------------------------
    # Group collected files into flights
    # --------------------------------------------------
    if processed_any:
        group_files_into_flights()

    print("\n==================================================")

    if processed_any:
        print("[V] Extraction completed successfully!")
        print(f"[V] All files are located at:\n    {os.path.abspath(LOCAL_DUMP_DIR)}")

    else:
        print("[!] No matched devices were processed.")

    print("=============================================================")
