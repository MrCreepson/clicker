from evdev import uinput, ecodes
import threading
import time

class Clicker:
    def __init__(self, time_sleep: float = 0.003, key: int = ecodes.BTN_LEFT) -> None:
        self.clicking = threading.Event()
        self.time_sleep = max(0.003, time_sleep)
        self.key = key
        print(f"[*] done clicker init")

    def start(self) -> None:
        pass
        self.clicking.set()
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        print("[*] started clicker")

    def stop(self) -> None:
        self.clicking.clear()
        print("[*] stopped clicker")
    
    def toggle(self) -> None:
        if self.clicking.is_set():
            self.stop()
        else:
            self.start()
    
    def _run(self) -> None:
        with uinput.UInput(events={ecodes.EV_KEY: [self.key]}) as ui:
            while self.clicking.is_set():
                ui.write(ecodes.EV_KEY, self.key, 1)
                ui.syn()
                ui.write(ecodes.EV_KEY, self.key, 0)
                ui.syn()
                time.sleep(self.time_sleep)