import os
import re
import shutil
import subprocess
from datetime import datetime

from config import LOCAL_DUMP_DIR, AndroidDevice


# Maximum allowed time difference between files in the same flight.
MAX_FLIGHT_TIME_DIFF = 120


def get_connected_serials() -> set[str]:
    """Return the serial numbers of all connected Android devices."""

    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            check=True,
        )

        connected_serials = set()

        # Skip the first line ("List of devices attached")
        # and collect only devices with the "device" status.
        for line in result.stdout.splitlines():
            match = re.match(r"^\s*(\S+)\s+device\s*$", line)

            if match:
                connected_serials.add(match.group(1))

        if not connected_serials:
            print("[!] No connected devices found.")

        return connected_serials

    except Exception as e:
        print(f"[!] Failed to detect connected devices: {e}")
        return set()


def get_file_type(filename: str) -> str | None:
    """
    Return the device type based on the filename prefix.

    Expected prefixes:
        RACER_
        TABLET_
        ISR_
    """

    upper_filename = filename.upper()

    for device_type in ("RACER", "TABLET", "ISR"):
        if upper_filename.startswith(f"{device_type}_"):
            return device_type

    return None


def group_files_into_flights() -> None:
    """
    Group collected log files into Flight folders.

    Rules:
    - A flight must contain at least 2 files.
    - Maximum 1 file from each device type.
    - Supported types: RACER, TABLET, ISR.
    - Maximum time difference between the first and last file:
      120 seconds.
    - If multiple files of the same type can belong to a flight,
      choose the largest file.
    - Prefer files in the same clock minute.
    - Files that cannot be matched remain in LOCAL_DUMP_DIR.
    """

    print("\n[--->] Grouping files into flights...")

    if not os.path.isdir(LOCAL_DUMP_DIR):
        print("[!] Local dump directory does not exist.")
        return

    files = []

    # Collect only files from the main dump directory.
    for filename in os.listdir(LOCAL_DUMP_DIR):

        file_path = os.path.join(
            LOCAL_DUMP_DIR,
            filename,
        )

        if not os.path.isfile(file_path):
            continue

        file_type = get_file_type(filename)

        if file_type is None:
            continue

        try:
            mtime = os.path.getmtime(file_path)
            file_size = os.path.getsize(file_path)
        except OSError:
            continue

        files.append(
            {
                "filename": filename,
                "path": file_path,
                "type": file_type,
                "mtime": mtime,
                "size": file_size,
            }
        )

    if len(files) < 2:
        print("[i] Not enough files to create flights.")
        return

    # Sort chronologically.
    files.sort(key=lambda x: x["mtime"])

    used = set()
    flights = []

    flight_number = 1

    for i, base_file in enumerate(files):

        if i in used:
            continue

        best_flight = [base_file]
        best_indexes = {i}

        # Find all candidates within 120 seconds from the base file.
        candidates_by_type = {}

        for j in range(i + 1, len(files)):

            if j in used:
                continue

            candidate = files[j]

            # Since files are sorted chronologically, once the
            # candidate is more than 120 seconds from the base,
            # there is no reason to continue.
            if (
                candidate["mtime"] - base_file["mtime"]
                > MAX_FLIGHT_TIME_DIFF
            ):
                break

            time_diff = abs(
                candidate["mtime"] - base_file["mtime"]
            )

            # Check whether the candidate is in the same clock minute.
            same_minute = (
                datetime.fromtimestamp(candidate["mtime"]).replace(
                    second=0,
                    microsecond=0,
                )
                ==
                datetime.fromtimestamp(base_file["mtime"]).replace(
                    second=0,
                    microsecond=0,
                )
            )

            candidate["time_diff"] = time_diff
            candidate["same_minute"] = same_minute

            # Keep candidates grouped by type.
            if candidate["type"] not in candidates_by_type:
                candidates_by_type[candidate["type"]] = []

            candidates_by_type[candidate["type"]].append(candidate)

        # ----------------------------------------------------------
        # Select the best candidate for each device type.
        #
        # Priority:
        # 1. Same clock minute
        # 2. Larger file size
        # 3. Smaller time difference
        # ----------------------------------------------------------
        for device_type, candidates in candidates_by_type.items():

            # Sort so the preferred file comes first.
            candidates.sort(
                key=lambda x: (
                    0 if x["same_minute"] else 1,
                    -x["size"],
                    x["time_diff"],
                )
            )

            selected_candidate = candidates[0]

            # Find the actual index of the selected candidate.
            selected_index = files.index(selected_candidate)

            # Check that adding this file does not exceed
            # the maximum total flight time range.
            new_flight = best_flight + [selected_candidate]

            new_min_time = min(
                file["mtime"]
                for file in new_flight
            )

            new_max_time = max(
                file["mtime"]
                for file in new_flight
            )

            if (
                new_max_time - new_min_time
                <= MAX_FLIGHT_TIME_DIFF
            ):
                best_flight.append(selected_candidate)
                best_indexes.add(selected_index)

                print(
                    f"[i] Selected {selected_candidate['filename']} "
                    f"({selected_candidate['size']} bytes) "
                    f"for type {device_type}"
                )

        # A flight must contain at least two files.
        if len(best_flight) < 2:
            continue

        # Create flight directory.
        while True:
            flight_name = f"Flight_{flight_number:03d}"

            flight_dir = os.path.join(
                LOCAL_DUMP_DIR,
                flight_name,
            )

            if not os.path.exists(flight_dir):
                break

            flight_number += 1

        os.makedirs(flight_dir)

        print(f"\n[+] Creating {flight_name}")

        for file_info in best_flight:

            destination = os.path.join(
                flight_dir,
                file_info["filename"],
            )

            try:
                shutil.move(
                    file_info["path"],
                    destination,
                )

                size_mb = file_info["size"] / (
                    1024 * 1024
                )

                print(
                    f"    {file_info['type']}: "
                    f"{file_info['filename']} "
                    f"({size_mb:.2f} MB)"
                )

            except OSError as e:
                print(
                    f"[!] Failed to move "
                    f"{file_info['filename']}: {e}"
                )

        used.update(best_indexes)
        flights.append(best_flight)

        flight_number += 1

    print(
        f"\n[+] Created {len(flights)} flight folders."
    )


def process_device(device: AndroidDevice) -> bool:
    """
    Pull log files from an Android device.

    Files are copied from the device to LOCAL_DUMP_DIR while:
    - preserving their original modification timestamps
    - adding the device prefix to each filename
    - keeping all files in the final dump directory
    """

    print(f"\n[--->] Starting copy from: {device.name}")

    # Make sure the destination directory exists.
    os.makedirs(LOCAL_DUMP_DIR, exist_ok=True)

    # Pull the entire Records directory from the device.
    #
    # -a = preserve file timestamps and permissions where possible.
    pull_command = [
        "adb",
        "-s",
        device.serial,
        "pull",
        "-a",
        device.remote_log_path,
        LOCAL_DUMP_DIR,
    ]

    print(f"[i] Running: {' '.join(pull_command)}")

    result = subprocess.run(
        pull_command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(
            f"[!] Failed to pull files from {device.name}: "
            f"{result.stderr.strip()}"
        )
        return False

    print("[+] ADB pull completed successfully.")

    # When ADB pulls a directory, it creates a local "Records"
    # directory inside LOCAL_DUMP_DIR.
    records_dir = os.path.join(
        LOCAL_DUMP_DIR,
        "Records",
    )

    if not os.path.isdir(records_dir):
        print("[i] No Records folder found.")
        print("[i] Files were already placed in the destination folder.")
        return True

    copied_count = 0

    # Walk through the Records directory recursively.
    # This also handles files located inside subdirectories.
    for root, _, filenames in os.walk(records_dir):

        for filename in filenames:

            source_path = os.path.join(
                root,
                filename,
            )

            # Add the device-specific prefix to prevent filename
            # collisions between different Android devices.
            if filename.startswith(
                f"{device.file_prefix}_"
            ):
                new_filename = filename
            else:
                new_filename = (
                    f"{device.file_prefix}_{filename}"
                )

            destination_path = os.path.join(
                LOCAL_DUMP_DIR,
                new_filename,
            )

            try:
                # Save the original modification timestamp before
                # moving the file to the final destination.
                original_mtime = os.path.getmtime(
                    source_path
                )

                # Move the file from Records/ to the final directory.
                os.rename(
                    source_path,
                    destination_path,
                )

                # Restore the original modification timestamp.
                os.utime(
                    destination_path,
                    (
                        original_mtime,
                        original_mtime,
                    ),
                )

                copied_count += 1

                print(
                    f"[+] {filename} -> {new_filename}"
                )

            except OSError as e:
                print(
                    f"[!] Failed to move "
                    f"{filename}: {e}"
                )

    # Remove the temporary Records directory if it is empty.
    try:
        os.rmdir(records_dir)
    except OSError:
        # The directory may not be empty if something failed to move.
        pass

    print(
        f"[+] Total REFF files copied from "
        f"{device.name}: {copied_count}"
    )

    return True
