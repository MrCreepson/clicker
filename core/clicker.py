from evdev import uinput, ecodes
import threading
import time

class Clicker:
    def __init__(self, time_sleep: float = 0.002, key: int = ecodes.BTN_LEFT) -> None:
        self.clicking = threading.Event()
        self.time_sleep = max(0.002, time_sleep)
        self.key = key
        print(f"[*] done clicker init")

    def start(self) -> None:
        print("[*] clicker start called")
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
 
    def update_settings(self, time_sleep: float, key: int) -> None:
        self.time_sleep = max(0.002, time_sleep)
        self.key = key
        print(f"[*] updated clicker settings: time_sleep={self.time_sleep}, key={self.key}")
    
    def _run(self) -> None:
        print("[*] clicker _run started")
        try:
            with uinput.UInput(events={ecodes.EV_KEY: [self.key]}) as ui:
                print(f"[*] uinput created for key {self.key}")
                while self.clicking.is_set():
                    ui.write(ecodes.EV_KEY, self.key, 1)
                    ui.syn()
                    time.sleep(self.time_sleep/2)
                    ui.write(ecodes.EV_KEY, self.key, 0)
                    ui.syn()
                    time.sleep(self.time_sleep/2)
        except Exception as e:
            print(f"[!] clicker error: {e}")