from evdev import ecodes

button = "KEY_KPMINUS"

start_button = getattr(ecodes, button)

print(start_button)