from pathlib import Path


def get_folders_in_downloads() -> list[Path]:
    downloads_path = Path.home() / "Downloads"

    excluded_suffixes = {
        ".app",
        ".download",
        ".bundle",
        ".framework",
    }

    folders = [
        path
        for path in downloads_path.iterdir()
        if path.is_dir() and path.suffix.lower() not in excluded_suffixes
    ]

    return [downloads_path, *folders]
