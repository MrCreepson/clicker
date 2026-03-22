from evdev import InputDevice, list_devices, ecodes

def find_keyboard(exclude_names) -> InputDevice | None:
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if not any(name in device.name for name in exclude_names):
            if ecodes.EV_KEY in device.capabilities():
                caps = device.capabilities()[ecodes.EV_KEY]
                if ecodes.KEY_A in caps and ecodes.KEY_SPACE in caps:
                    return device
    return None