import os

from config import DEVICES_REGISTRY, LOCAL_DUMP_DIR
from collector import (
    get_connected_serials,
    process_device,
    group_files_into_flights,
)


def main():
    print("==================================================")
    print("       Starting Reff Extraction                   ")
    print("==================================================")

    print(
        f"[i] Saving files to path:\n"
        f"    {os.path.abspath(LOCAL_DUMP_DIR)}\n"
    )

    os.makedirs(LOCAL_DUMP_DIR, exist_ok=True)

    connected_serials = get_connected_serials()

    if not connected_serials:
        print("[-] No connected ADB devices found.")
        return

    print(
        f"[+] Total devices connected: "
        f"{len(connected_serials)}"
    )

    processed_any = False

    for device in DEVICES_REGISTRY:
        if device.serial in connected_serials:
            process_device(device)
            processed_any = True

        else:
            print(
                f"[i] {device.name} "
                f"(Serial: {device.serial}) "
                f"- Not connected, skipping."
            )

    # --------------------------------------------------
    # Group collected files into flights
    # --------------------------------------------------
    if processed_any:
        group_files_into_flights()

    print("\n==================================================")

    if processed_any:
        print("[V] Extraction completed successfully!")
        print(
            f"[V] All files are located at:\n"
            f"    {os.path.abspath(LOCAL_DUMP_DIR)}"
        )

    else:
        print("[!] No matched devices were processed.")

    print("=============================================================")


if __name__ == "__main__":
    main()