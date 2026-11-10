from pydantic import BaseModel
from typing import Optional, Dict, Any


# Esta es la que ya tenías para el settings.json
class AppConfig(BaseModel):
    api_port: int
    login_url: str
    target_variable: str
    browser_visible: bool


# Esta es la NUEVA para recibir datos desde Postman
class TokenRequest(BaseModel):
    login_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    registration_data: Optional[Dict[str, Any]] = None
