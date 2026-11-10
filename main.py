import uvicorn
import os
import sys
import threading
import webbrowser
from PIL import Image
from pystray import Icon, MenuItem, Menu
from src.api.app import app
from src.utils.config_loader import load_settings  # Un helper para leer el JSON


def resource_path(relative_path: str) -> str:
    """Obtiene la ruta absoluta al recurso, compatible con PyInstaller y entorno dev."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def start_api():
    settings = load_settings()
    uvicorn.run(app, host="127.0.0.1", port=settings["api_port"], log_level="info")


if __name__ == "__main__":
    # 1. Lanzar API en segundo plano
    threading.Thread(target=start_api, daemon=True).start()

    # 2. Configurar Icono en la bandeja
    icon_file = resource_path(os.path.join("resource", "checked.png"))
    try:
        img = Image.open(icon_file)
    except Exception as e:
        print(f"Error cargando icono desde {icon_file}: {e}")
        img = Image.new("RGB", (64, 64), color=(0, 100, 255))

    settings = load_settings()

    icon = Icon(
        "WebTokenTool",
        img,
        "WebTokenTool - Capturador de Tokens",
        menu=Menu(
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
