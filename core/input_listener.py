from core.devices import find_keyboard
from evdev import ecodes, InputDevice
import threading

class InputListener:
    def __init__(self, on_toggle, device: InputDevice, key: int = ecodes.KEY_KPMINUS) -> None:
        self.on_toggle = on_toggle
        self.keyboard = device
        self.key = key
        print("[/] done listener init")
    
    def start(self) -> None:
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        print("[/] listener clicker")

    def _run(self) -> None:
        for event in self.keyboard.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:
                if event.code == self.key:
                    print("[/] toggle signal")
                    self.on_toggle()
                    