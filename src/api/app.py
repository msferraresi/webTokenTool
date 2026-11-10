from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from src.api.schemas import AppConfig, TokenRequest
from src.utils.config_loader import load_settings, save_settings
from src.core.token_extractor import TokenExtractor  # Tu clase de Selenium
import os

app = FastAPI(title="WebTokenTool API")


# 1. Endpoints de Configuración
@app.get("/api/config")
def get_config():
    return load_settings()


@app.post("/api/config")
def update_config(config: AppConfig):
    save_settings(config.dict())
    return {"status": "success", "message": "Configuración actualizada"}


# 2. El Endpoint que usará Postman
@app.post("/get-token")
def get_token(request_data: TokenRequest):
    settings = load_settings()

    execution_config = {
        "login_url": request_data.login_url,
        "username": request_data.username,
        "password": request_data.password,
        "browser_visible": settings.get("browser_visible", True),
        "target_variable": settings.get("target_variable", "accessToken"),
    }

    extractor = TokenExtractor(execution_config)

    if request_data.registration_data:
        print("[Python] Detectado flujo de registro adaptado. Iniciando Selenium...")
        print(
            f"🚨 [Python DEBUG] La URL recibida es exactamente: '{request_data.login_url}'"
        )
        # Levantamos el driver pasándole la URL y los datos nuevos
        captcha_token = extractor.execute_universal_captcha_extractor(
            request_data.login_url, request_data.registration_data
        )
        return {
            "accessToken": "REGISTRATION_FLOW",  # Postman no necesita el token de login acá
            "captchaResponse": captcha_token,
        }
    else:
        token = extractor.run_capture()

        if token:
            return {"status": "success", "accessToken": token}
        else:
            raise HTTPException(status_code=500, detail="No se pudo capturar el token")


# 3. Servir el Dashboard (Static Files)
# Asumiendo que creaste la carpeta 'static' en la raíz
static_path = os.path.join(os.getcwd(), "static")
if os.path.exists(static_path):
    app.mount(
        "/dashboard", StaticFiles(directory=static_path, html=True), name="static"
    )
