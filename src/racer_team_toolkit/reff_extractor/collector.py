import os
import shutil
from datetime import datetime
from typing import Optional

from racer_team_toolkit.adb import run_adb_command
from racer_team_toolkit.config import (
    LOCAL_DUMP_DIR,
    MAX_FLIGHT_TIME_DIFF,
    MAX_VIDEO_TIME_DIFF,
    SUPPORTED_DEVICE_TYPES,
    VIDEO_REMOTE_PATH,
    AndroidDevice,
)


def get_file_type(filename: str) -> Optional[str]:
    """
    Return the device type based on the filename prefix.

    Expected prefixes:
        RACER_
        TABLET_
        ISR_
    """

    upper_filename = filename.upper().replace(" ", "_")

    for device_type in SUPPORTED_DEVICE_TYPES:
        if upper_filename.startswith(f"{device_type}_"):
            return device_type

    return None


def get_video_files() -> list[dict]:
    """Return downloaded videos from the main dump directory."""

    videos = []

    for filename in os.listdir(LOCAL_DUMP_DIR):
        if not filename.upper().startswith("VIDEO_"):
            continue

        file_path = os.path.join(LOCAL_DUMP_DIR, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            videos.append(
                {
                    "filename": filename,
                    "path": file_path,
                    "mtime": os.path.getmtime(file_path),
                    "size": os.path.getsize(file_path),
                }
            )
        except OSError:
            continue

    return videos


def attach_videos_to_flight(flight_dir: str, flight_files: list[dict], videos: list[dict]) -> int:
    """Move videos within the flight time limit into a flight directory."""

    flight_times = [file_info["mtime"] for file_info in flight_files]
    matching_videos = [
        video
        for video in videos
        if min(abs(video["mtime"] - flight_time) for flight_time in flight_times)
        <= MAX_VIDEO_TIME_DIFF
    ]

    for video in matching_videos:
        try:
            shutil.move(video["path"], os.path.join(flight_dir, video["filename"]))
        except OSError as error:
            print(f"[!] Failed to move {video['filename']}: {error}")
        else:
            print(f"    VIDEO: {video['filename']}")

    return len(matching_videos)


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
            if candidate["mtime"] - base_file["mtime"] > MAX_FLIGHT_TIME_DIFF:
                break

            time_diff = abs(candidate["mtime"] - base_file["mtime"])

            # Check whether the candidate is in the same clock minute.
            same_minute = datetime.fromtimestamp(candidate["mtime"]).replace(
                second=0,
                microsecond=0,
            ) == datetime.fromtimestamp(base_file["mtime"]).replace(
                second=0,
                microsecond=0,
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

            new_min_time = min(file["mtime"] for file in new_flight)

            new_max_time = max(file["mtime"] for file in new_flight)

            if new_max_time - new_min_time <= MAX_FLIGHT_TIME_DIFF:
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
            flight_name = f"Flight_{flight_number:02d}"

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

                size_mb = file_info["size"] / (1024 * 1024)

                print(f"    {file_info['type']}: {file_info['filename']} ({size_mb:.2f} MB)")

            except OSError as e:
                print(f"[!] Failed to move {file_info['filename']}: {e}")

        attach_videos_to_flight(flight_dir, best_flight, get_video_files())

        used.update(best_indexes)
        flights.append(best_flight)

        flight_number += 1

    print(f"\n[+] Created {len(flights)} flight folders.")


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

    result = run_adb_command(pull_command)

    if result.returncode != 0:
        print(f"[!] Failed to pull files from {device.name}: {result.stderr.strip()}")
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
        return pull_videos(device)

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
            if filename.startswith(f"{device.file_prefix}_"):
                new_filename = filename
            else:
                new_filename = f"{device.file_prefix}_{filename}"

            destination_path = os.path.join(
                LOCAL_DUMP_DIR,
                new_filename,
            )

            try:
                # Save the original modification timestamp before
                # moving the file to the final destination.
                original_mtime = os.path.getmtime(source_path)

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

                print(f"[+] {filename} -> {new_filename}")

            except OSError as e:
                print(f"[!] Failed to move {filename}: {e}")

    # Remove empty temporary directories, including nested directories.
    for root, _, _ in os.walk(records_dir, topdown=False):
        try:
            os.rmdir(root)
        except OSError:
            # Keep directories that still contain files after a failed move.
            pass

    print(f"[+] Total REFF files copied from {device.name}: {copied_count}")

    pull_videos(device)

    return True


def pull_videos(device: AndroidDevice) -> bool:
    """Pull screen recordings and flatten them into the dump directory."""

    pull_command = [
        "adb",
        "-s",
        device.serial,
        "pull",
        "-a",
        VIDEO_REMOTE_PATH,
        LOCAL_DUMP_DIR,
    ]

    result = run_adb_command(pull_command)

    if result.returncode != 0:
        print(f"[i] No screen videos pulled from {device.name}.")
        return False

    videos_dir = os.path.join(LOCAL_DUMP_DIR, "Screen-Videos")

    if not os.path.isdir(videos_dir):
        print(f"[i] No screen videos found for {device.name}.")
        return True

    for root, _, filenames in os.walk(videos_dir):
        for filename in filenames:
            source_path = os.path.join(root, filename)
            destination_name = f"VIDEO_{device.file_prefix}_{filename}"
            destination_path = os.path.join(LOCAL_DUMP_DIR, destination_name)

            try:
                original_mtime = os.path.getmtime(source_path)
                shutil.move(source_path, destination_path)
                os.utime(destination_path, (original_mtime, original_mtime))
                print(f"[+] Video: {filename} -> {destination_name}")
            except OSError as error:
                print(f"[!] Failed to move video {filename}: {error}")

    for root, _, _ in os.walk(videos_dir, topdown=False):
        try:
            os.rmdir(root)
        except OSError:
            pass

    return True
