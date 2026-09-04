from pathlib import Path


def upload_jar(path: Path) -> bool:
    """Upload a JAR file to a connected Linux device using SSH"""


def restart_jar() -> bool:
    """Restart a JAR file on a connected Linux device using SSH"""


def check_server_status() -> bool:
    """check if the server is connected to the computer"""
    return True  # Placeholder implementation, replace with actual server check logic


def check_if_jar_exists_in_folder(folder_path: Path) -> bool:
    """Check if a JAR file exists in the specified folder."""

    jar_files = list(folder_path.glob("*.jar"))
    return len(jar_files) > 0
