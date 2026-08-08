import json

def load_settings():
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
    except FileNotFoundError:
        print("Settings file not found. Using default values.")
        settings = {}

    return settings

def main():
    settings = load_settings()

    print(f"Loaded settings: {json.dumps(settings['button'], indent=4)}")

if __name__ == "__main__":
    main()