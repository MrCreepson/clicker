import time
from evdev import ecodes
import threading

from core.clicker import Clicker
from core.input_listener import InputListener
from core.devices import find_keyboard

"""
TODO:   add JSON settings
        add PySide6 ui
        add custom button to asign to click and listen 
"""

exclude_names = ["gsr-ui virtual keyboard", "Acer NKW201 Keyboard", "XP-Pen"]

def main():
    clicker = Clicker(key=ecodes.BTN_LEFT)

    keyboard = find_keyboard(exclude_names=exclude_names)
    assert keyboard is not None, "Keyboard not found"
    keyboard.name = keyboard.name.strip()
    print(f"[m] Found device: Listening to: {keyboard.name}")

    listener = InputListener(on_toggle=clicker.toggle, device=keyboard, key=ecodes.KEY_KPMINUS)
    listener.start()

    threading.Event().wait()

if __name__ == "__main__":
    main()