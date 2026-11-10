```markdown
# WebTokenTool 🚀

**WebTokenTool** es un orquestador técnico diseñado para automatizar la captura de accessTokens (JWT) en aplicaciones de Federación Patronal que presentan barreras para la automatización tradicional, como el uso de CAPTCHA o flujos de autenticación legados.

El proyecto permite que un desarrollador o QA, trabajando desde Postman, pueda obtener un token válido sin tener que realizar el proceso de login manual repetitivo, integrando Selenium y FastAPI como un puente de automatización.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.10+

Framework API: FastAPI (para una comunicación asíncrona de alto rendimiento)

Automatización: Selenium WebDriver con Chrome DevTools Protocol (CDP)

Gestión de Drivers: WebDriver Manager (Chrome)

Orquestación: Postman Pre-request Scripts

🏗️ Arquitectura del Sistema
El flujo de trabajo se divide en tres capas de responsabilidad:

Capa de Cliente (Postman): El script de pre-requisito evalúa si el token en caché (Global Variables) ha expirado. Si es así, despacha una solicitud POST al middleware local enviando el contexto del proyecto y las credenciales.

Capa de Middleware (FastAPI): Recibe la solicitud, valida los parámetros (URL, usuario, contraseña) y lanza el motor de extracción.

Capa de Automatización (Selenium): Abre una instancia de Chrome, navega al ambiente solicitado (Dev o Test), inyecta las credenciales en los campos username y contraseña, y monitorea el tráfico de red hasta capturar la respuesta del servidor con el token.

📂 Estructura del Proyecto
Plaintext
WEBTOKENTOOL/
├── src/
│   ├── api/
│   │   ├── app.py           # Endpoints de la API y lógica de merge de config
│   │   └── schemas.py       # Contratos de datos (AppConfig y TokenRequest)
│   └── core/
│       └── token_extractor.py # Motor Selenium con intercepción de red
├── main.py                  # Punto de entrada del servidor Uvicorn
├── settings.json            # Configuración base (puertos, visibilidad del browser)
└── requirements.txt         # Dependencias del ecosistema Python
🚀 Configuración e Integración
1. Preparación del Entorno Python
Bash
pip install -r requirements.txt
python main.py
1. Configuración en Postman
Para que el script de Postman sepa cómo interactuar con la herramienta, el Request debe tener configurados los siguientes Headers:

X-Type-Project: Debe ser old para disparar este flujo.

X-Api-Context: El nombre del microservicio (ej. reclamos, juicios).

X-Username: Usuario de Fedpat.

X-Password: Contraseña de Fedpat.

3. Lógica de Autocompletado
La herramienta busca automáticamente los siguientes selectores en la web de Fedpat:

ID: username

ID: contraseña

Si el sistema detecta que estas credenciales vienen en el request de Postman, las inyectará automáticamente, dejando al usuario únicamente la tarea de resolver el desafío visual (CAPTCHA).

📊 Ciclo de Vida del Token
Para optimizar recursos, la herramienta implementa una política de Lazy Refresh:

Validación de Ambiente: Si cambias de ambiente en Postman (ej. de Dev a Test), el token se invalida automáticamente.

Cálculo de Expiración: Se calcula el expireAt (basado en el expires_in del servidor o 1 hora por defecto).

Persistencia: El token se almacena en pm.globals para que pueda ser reutilizado por todos los requests de la colección sin volver a abrir el navegador.

📝 Notas de Mantenimiento (Senior Tips)
Headless Mode: Se puede cambiar en settings.json para que el navegador no sea visible, aunque se recomienda visible para resolver el CAPTCHA.

Timeouts: El extractor tiene un tiempo de espera de 300 segundos para dar margen a la resolución manual del login.

Seguridad: Las credenciales nunca se almacenan en el disco; solo viajan en memoria desde Postman hacia la instancia volátil de Selenium.

Desarrollado para la optimización de procesos de desarrollo en entornos complejos.