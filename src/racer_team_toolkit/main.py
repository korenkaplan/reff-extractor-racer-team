from racer_team_toolkit.apk_installer.main import main as run_apk_installer_main
from racer_team_toolkit.jar_management.main import main as run_jar_management_main
from racer_team_toolkit.reff_extractor.main import main as run_reff_and_videos_extractor_main
from racer_team_toolkit.ui.functions import print_header, select_menu


def main() -> None:
    while True:
        print_header("Racer Team Toolkit")

        choice = select_menu(
            "Select a tool:",
            [
                "REFF & Video Extractor",
                "APK Installer",
                "JAR Management",
                "Exit",
            ],
        )

        if choice == "REFF & Video Extractor":
            # run extractor
            run_reff_and_videos_extractor_main()
            break

        elif choice == "APK Installer":
            # run APK installer
            run_apk_installer_main()

        elif choice == "JAR Management":
            # run JAR management
            run_jar_management_main()

        elif choice == "Exit" or choice is None:
            break


if __name__ == "__main__":
    main()
