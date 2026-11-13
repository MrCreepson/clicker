import time
from evdev import ecodes
import threading
import json
import os
import pwd
import grp

from core.clicker import Clicker
from core.input_listener import InputListener
from core.devices import find_keyboard, find_mouse

import sys
from ui.window import MyWidget
from core.proxy import StdoutProxy
from io import StringIO
from PySide6 import QtWidgets

from setproctitle import setproctitle

setproctitle("clicker")

"""
TODO
        Easy .desktop implementation

        add or ask user to add to input group

        clear all the test and unnecessary files

        upgrade PySide6 ui

        positional clicker
            "postition": [{
                "is_on": false,
                "x": 0,
                "y": 0
            }]

        change betwen hold and click for clicker
                "hold": false,
"""

def get_group_names(username):
    user_info = pwd.getpwnam(username)
    gids = os.getgrouplist(username, user_info.pw_gid)

    group_names=[]
    for gid in gids:
        try:
            group_info = grp.getgrgid(gid)
            group_names.append(group_info.gr_name)
        except KeyError:
            group_names.append(str(gid))
    return group_names

username = pwd.getpwuid(os.getuid()).pw_name
groups = get_group_names(username)


if "input" not in groups :
    raise PermissionError("Add yourself to input groups (sudo usermod -aG input $USER)")

device_types = ["keyboard", "mouse"]



def init_window(settings_path):
    app = QtWidgets.QApplication(sys.argv)
    stdout_proxy = StdoutProxy()
    sys.stdout = stdout_proxy
    widget = MyWidget(stdout_proxy=stdout_proxy, config_file=settings_path, reload_callback=None)
    widget.show()
    return app, widget, stdout_proxy

def load_settings(settings_path):

    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
    except FileNotFoundError:
        print("Settings file not found. Using default values.")
        settings = {}

    exclude_keyboard_names = settings.get("exclude_keyboard_names", ["gsr-ui virtual keyboard", "Acer NKW201 Keyboard", "XP-Pen"])
    exclude_mouse_names = settings.get("exclude_mouse_names", ["Keyboard", "Acer", "XP-Pen"])
    
    button_settings_raw = settings.get("button", [{}])
    if isinstance(button_settings_raw, list) and button_settings_raw:
        button_settings = button_settings_raw[0]
    else:
        button_settings = button_settings_raw if isinstance(button_settings_raw, dict) else {}

    device_type = button_settings.get("device_type", "mouse")
    start_button = button_settings.get("input")
    click_button = button_settings.get("output", "BTN_LEFT")
    
    time_settings_raw = settings.get("time", [{}])
    if isinstance(time_settings_raw, list) and time_settings_raw:
        time_settings = time_settings_raw[0]
    else:
        time_settings = time_settings_raw if isinstance(time_settings_raw, dict) else {}
    time_seconds = time_settings.get("s", 0)
    time_milliseconds = time_settings.get("ms", 4)
    time_sleep = time_seconds + (time_milliseconds / 1000)

    start_button_keycode = getattr(ecodes, start_button, ecodes.BTN_EXTRA)
    click_button_keycode = getattr(ecodes, click_button, ecodes.BTN_LEFT)
    reload_on_toggle = settings.get("reload_on_toggle", False)
    return exclude_keyboard_names, exclude_mouse_names, device_type, start_button_keycode, click_button_keycode, start_button, click_button, time_sleep, reload_on_toggle


def main():
    # Initialize UI first so all logs are captured
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(base_dir, "settings.json")
    app, widget, stdout_proxy = init_window(settings_path)
    
    # Now all print() calls go to the UI
    exclude_keyboard_names, exclude_mouse_names, device_type, start_button_keycode, click_button_keycode, start_button, click_button, time_sleep, reload_on_toggle = load_settings(settings_path)

    if device_type == "keyboard":
        device = find_keyboard(exclude_keyboard_names=exclude_keyboard_names)
    elif device_type == "mouse":
        device = find_mouse(exclude_mouse_names=exclude_mouse_names)
    else:
        raise ValueError(f"Invalid device type: {device_type}")
    assert device is not None, "Device not found."

    device.name = device.name.strip()
    print(f"[m]  Found device:\n├── Listening device: {device.name} {{{device.path}}},\n├── Listening button: {start_button},\n├── Clicking with: {click_button},\n└── Click delay: {time_sleep}s")

    clicker = Clicker(key=click_button_keycode, time_sleep=time_sleep)
    
    def temp_on_toggle():
        pass  # placeholder
    
    listener = InputListener(on_toggle=temp_on_toggle, device=device, key=start_button_keycode)
    listener.start()
    
    def reload_settings_callback():
        nonlocal start_button_keycode, device_type, device, listener
        # Always reload all settings for manual reload
        exclude_keyboard_names_new, exclude_mouse_names_new, device_type_new, start_button_keycode_new, click_button_keycode_new, start_button_new, click_button_new, time_sleep_new, _ = load_settings()
        if device_type_new != device_type:
            print(f"[*] Switching device type to {device_type_new}")
            listener.stop()
            if device_type_new == "keyboard":
                device = find_keyboard(exclude_keyboard_names=exclude_keyboard_names_new)
            elif device_type_new == "mouse":
                device = find_mouse(exclude_mouse_names=exclude_mouse_names_new)
            else:
                raise ValueError(f"Invalid device type: {device_type_new}")
            assert device is not None, f"New device not found for {device_type_new}"
            device.name = device.name.strip()
            device_type = device_type_new
            listener = InputListener(on_toggle=listener.on_toggle, device=device, key=start_button_keycode_new)
            listener.start()
            print(f"[*] Switched to device: {device.name}")
        if start_button_keycode_new != start_button_keycode:
            listener.key = start_button_keycode_new
            start_button_keycode = start_button_keycode_new
            print(f"[*] Updated start button to {start_button_new}")
        clicker.update_settings(time_sleep_new, click_button_keycode_new)
        print("[*] Settings reloaded.")
    
    def on_toggle():
        nonlocal start_button_keycode, device_type, device, listener
        print(f"[*] on_toggle called, clicking: {clicker.clicking.is_set()}")
        try:
            if clicker.clicking.is_set():
                clicker.stop()
            else:
                print("[*] starting clicker")
                if reload_on_toggle:
                    # Reload all settings
                    _, _, device_type_new, start_button_keycode_new, click_button_keycode_new, start_button_new, click_button_new, time_sleep_new, _ = load_settings(settings_path)
                    if device_type_new != device_type:
                        print(f"[!] Device type changed to {device_type_new}, use reload button to apply.")
                    if start_button_keycode_new != start_button_keycode:
                        listener.key = start_button_keycode_new
                        start_button_keycode = start_button_keycode_new
                        print(f"[*] Updated start button to {start_button_new}")
                    clicker.update_settings(time_sleep_new, click_button_keycode_new)
                else:
                    # Only reload time and click_button
                    _, _, _, _, click_button_keycode_new, _, _, time_sleep_new, _ = load_settings(settings_path)
                    clicker.update_settings(time_sleep_new, click_button_keycode_new)
                clicker.start()
        except Exception as e:
            print(f"[!] on_toggle error: {e}")
    
    listener.on_toggle = on_toggle
    widget.reload_button.clicked.connect(reload_settings_callback)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()