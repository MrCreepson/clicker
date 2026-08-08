from evdev import InputDevice, list_devices, ecodes

def find_devices() -> InputDevice | None:
    devices = [InputDevice(path) for path in list_devices()]
    return devices

def main():
    devices = find_devices()
    for device in devices:
        print(device)

if __name__ == "__main__":
    main()