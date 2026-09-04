from racer_team_toolkit.adb import get_conneccted_android_devices, get_connected_serials


def main() -> None:
    print("Running adb __init__.py test script...")
    android_devices = get_conneccted_android_devices()
    serials = get_connected_serials()
    print(f"Connected Android Devices: {android_devices}")
    print(f"Connected Serials: {serials}")


if __name__ == "__main__":
    main()
