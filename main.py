import threading
import uvicorn
import os
import webbrowser
from pystray import Icon, MenuItem, Menu
from PIL import Image
from src.api.app import app  # Tu instancia de FastAPI
from src.utils.config_loader import load_settings  # Un helper para leer el JSON


def start_api():
    settings = load_settings()
    uvicorn.run(app, host="127.0.0.1", port=settings["api_port"], log_level="info")


if __name__ == "__main__":
    # 1. Lanzar API en segundo plano
    threading.Thread(target=start_api, daemon=True).start()

    # 2. Configurar Icono en la bandeja
    try:
        img = Image.open("resource/checked.png")
    except:
        img = Image.new("RGB", (64, 64), color=(0, 100, 255))

    settings = load_settings()

    icon = Icon(
        "WebTokenTool",
        img,
        "WebTokenTool - Capturador de Tokens",
        menu=Menu(
            # MenuItem(
            #     "Configuración (Dashboard)",
            #     lambda: webbrowser.open(
            #         f"http://127.0.0.1:{settings['api_port']}/dashboard"
            #     ),
            # ),
            MenuItem(
                "Ver API (Swagger)",
                lambda: webbrowser.open(
                    f"http://127.0.0.1:{settings['api_port']}/docs"
                ),
            ),
            MenuItem("Salir", lambda i: os._exit(0)),
        ),
    )

    icon.run()
