import json
import os

SETTINGS_PATH = "config/settings.json"


def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        # Valores por defecto si el archivo no existe
        return {
            "api_port": 5000,
            "login_url": "https://self-dev.fedpat.com.ar/reclamos/ui#/login",
            "target_variable": "accessToken",
            "browser_visible": True,
        }
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)


def save_settings(config_dict):
    os.makedirs("config", exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(config_dict, f, indent=4)
