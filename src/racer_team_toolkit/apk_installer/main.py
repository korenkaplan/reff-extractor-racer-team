from racer_team_toolkit.adb import get_connected_serials
from racer_team_toolkit.apk_installer.functions import get_folders_in_downloads
from racer_team_toolkit.config import APK_INSTALLER_HEADER
from racer_team_toolkit.ui.functions import print_error, print_header, select_menu_tuple

FOLDER_IN_DOWNLOADS_WITH_FULL_PATH = get_folders_in_downloads()
MENU_CHOICES = [path.name for path in FOLDER_IN_DOWNLOADS_WITH_FULL_PATH]


def main() -> None:
    print_header("APK Installer!")
    connected_devices = get_connected_serials()

    # check if there are any connected devices
    if len(connected_devices) == 0:
        print_error("No connected ADB devices found.")
        # wait for user input before returning to main menu

        # clear the console and return to main menu

    # Print Menu and get user choice
    choice_index, user_choice = select_menu_tuple(APK_INSTALLER_HEADER, MENU_CHOICES)

    # Use the choice_index to get the corresponding folder path

    # Get all the connected android devices

    # for each connected device do the following:

    # 1. Check whether the folder contains the device's APK file.
    #    The filename comes from the device's apk_file_name attribute.

    # 2. If not, report that the APK is missing and continue.

    # 3. If yes, uninstall the app and install the APK with ADB.

    # 4. Report that the APK was installed successfully.

    # 5. When complete, wait for input and return to the main menu.
