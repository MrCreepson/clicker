from evdev import InputDevice, list_devices, ecodes

def find_keyboard(exclude_keyboard_names) -> InputDevice | None:
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if not any(name in device.name for name in exclude_keyboard_names):
            if ecodes.EV_KEY in device.capabilities():
                caps = device.capabilities()[ecodes.EV_KEY]
                if ecodes.KEY_A in caps and ecodes.KEY_SPACE in caps:
                    return device
    return None

def find_mouse(exclude_mouse_names) -> InputDevice | None:
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if not any(name in device.name for name in exclude_mouse_names):
            if ecodes.EV_REL in device.capabilities():
                caps = device.capabilities()[ecodes.EV_REL]
                if ecodes.REL_X in caps and ecodes.REL_Y in caps:
                    return device
    return None

def main():
    exclude_keyboard_names = ["gsr-ui virtual keyboard", "Acer NKW201 Keyboard", "XP-Pen"]
    exclude_mouse_names = ["Keyboard", "Acer"]

    keyboard = find_keyboard(exclude_keyboard_names=exclude_keyboard_names)
    assert keyboard is not None, "Keyboard not found"
    keyboard.name = keyboard.name.strip()
    print(keyboard.name)

    mouse = find_mouse(exclude_mouse_names=exclude_mouse_names)
    assert mouse is not None, "Keyboard not found"
    mouse.name = mouse.name.strip()
    print(mouse.name)

    for event in mouse.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            print(event.code, ecodes.BTN_EXTRA)

if __name__ == "__main__":
    main()