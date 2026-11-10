import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class TokenExtractor:
    def __init__(self, config):
        self.config = config
        self.token = None
        self.driver = None  # Dejamos la propiedad declarada en el constructor

    def init_driver(self):
        """
        Método centralizado para inicializar el driver de Chrome con sus opciones.
        Reutiliza la configuración exacta que ya tenías funcionando de manera aislada.
        """
        options = webdriver.ChromeOptions()
        # Habilitamos el log de performance para interceptar el tráfico de red
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        # Configuramos visibilidad según el dashboard
        if not self.config.get("browser_visible", True):
            options.add_argument("--headless")

        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        return self.driver

    def run_capture(self):
        # 💡 Modificado de manera segura: si el driver no existe, lo inicializa llamando al nuevo método
        driver = self.driver if self.driver else self.init_driver()

        try:
            driver.get(self.config["login_url"])
            print(f"🌍 Navegando a: {self.config['login_url']}")

            # --- NUEVA LÓGICA DE AUTOCOMPLETADO ---
            if self.config.get("username") and self.config.get("password"):
                try:
                    # Damos un respiro para que el DOM cargue
                    time.sleep(2)

                    # Buscamos por NAME (asegurate que en Fedpat se llamen así)
                    user_field = driver.find_element(By.ID, "username")
                    pass_field = driver.find_element(By.ID, "contraseña")

                    user_field.send_keys(self.config["username"])
                    pass_field.send_keys(self.config["password"])

                    print("[Extractor] Credenciales autocompletadas.")
                except Exception as e:
                    print(f"[Extractor] No se pudo autocompletar: {e}")
            # --------------------------------------

            # Tiempo máximo de espera configurado en settings.json
            timeout = time.time() + self.config.get("timeout_seconds", 300)
            target_var = self.config.get("target_variable", "accessToken")

            while time.time() < timeout:
                logs = driver.get_log("performance")
                for entry in logs:
                    try:
                        log_json = json.loads(entry["message"])
                        message = log_json.get("message", {})
                        method = message.get("method", "")

                        # Detectamos cuando una respuesta de red ha llegado
                        if method == "Network.responseReceived":
                            response = message.get("params", {}).get("response", {})
                            url = response.get("url", "")

                            # Filtramos por palabras clave de login/auth
                            if "login" in url.lower() or "auth" in url.lower():
                                request_id = message["params"]["requestId"]

                                # Extraemos el cuerpo de la respuesta usando CDP (Chrome DevTools Protocol)
                                response_body = driver.execute_cdp_cmd(
                                    "Network.getResponseBody", {"requestId": request_id}
                                )
                                body = response_body.get("body", "")

                                if body:
                                    data = json.loads(body)
                                    if target_var in data:
                                        self.token = data[target_var]
                                        print(
                                            f"✅ Token '{target_var}' capturado exitosamente."
                                        )
                                        return self.token
                    except Exception:
                        continue  # Errores silenciosos para no romper el loop de monitoreo

                time.sleep(1)  # Evitamos saturar el CPU

        except Exception as e:
            print(f"❌ Error durante la captura: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None  # Reseteamos la instancia tras destruirla

        return None

    def execute_universal_captcha_extractor(self, url, data):
        driver = (
            self.driver
            if hasattr(self, "driver") and self.driver
            else self.init_driver()
        )

        try:
            driver.get(url)
            # Le damos 3 segundos completos para que Angular termine de compilar y renderizar el DOM
            time.sleep(3)

            try:
                # ==========================================
                # ESTRATEGIA A: REGISTRO DE ABOGADOS
                # ==========================================
                if "registro-abogados" in url:
                    print(
                        "[Python] Detectada página de Abogados Angular. Completando campos..."
                    )

                    # Usamos selectores CSS basados en 'formcontrolname' que son estáticos en Angular
                    if "name" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='nombre']"
                        ).send_keys(data["name"])
                    if "surname" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='apellido']"
                        ).send_keys(data["surname"])
                    if "dni" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='dni']"
                        ).send_keys(str(data["dni"]))
                    if "cuit" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='cuit']"
                        ).send_keys(str(data["cuit"]))
                    if "email" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='email']"
                        ).send_keys(data["email"])

                    # Domicilio de Abogados (Mapeamos según el HTML de este formulario)
                    if "address" in data and data["address"]:
                        addr = data["address"]
                        if "street" in addr:
                            driver.find_element(
                                By.CSS_SELECTOR, "input[formcontrolname='calle']"
                            ).send_keys(addr["street"])
                        if "number" in addr:
                            driver.find_element(
                                By.CSS_SELECTOR, "input[formcontrolname='num']"
                            ).send_keys(str(addr["number"]))
                        if "floor" in addr:
                            driver.find_element(
                                By.CSS_SELECTOR, "input[formcontrolname='piso']"
                            ).send_keys(str(addr["floor"]))
                        if "flat" in addr:
                            driver.find_element(
                                By.CSS_SELECTOR, "input[formcontrolname='depto']"
                            ).send_keys(addr["flat"])

                        if "province" in addr:
                            try:
                                print(
                                    f"[Python Combo] Abriendo mat-select de Provincia..."
                                )
                                # Buscamos el componente mat-select de la provincia y le damos clic
                                combo_provincia = driver.find_element(
                                    By.CSS_SELECTOR,
                                    "mat-select[formcontrolname='provincia']",
                                )
                                combo_provincia.click()
                                time.sleep(
                                    1.5
                                )  # Margen para que se despliegue el overlay flotante

                                # Buscamos la opción por el texto que viene de Postman (ej: "BUENOS AIRES")
                                texto_provincia = addr["province"].upper().strip()
                                opcion_target = driver.find_element(
                                    By.XPATH,
                                    f"//mat-option//span[contains(text(), '{texto_provincia}')]",
                                )
                                opcion_target.click()
                                print(
                                    f"[Python Combo] Selección exitosa: {texto_provincia}"
                                )
                                time.sleep(1)  # Esperamos que el clic asiente la UI
                            except Exception as e_prov:
                                print(
                                    f"[Python Combo] Error seleccionando provincia: {e_prov}"
                                )

                        if "locality" in addr:
                            try:
                                print(
                                    f"[Python Combo] Abriendo mat-select de Localidad..."
                                )
                                # Buscamos el componente mat-select de la localidad y le damos clic
                                combo_localidad = driver.find_element(
                                    By.CSS_SELECTOR,
                                    "mat-select[formcontrolname='localidad']",
                                )
                                combo_localidad.click()
                                time.sleep(
                                    1.5
                                )  # Margen para que renderice la lista según la provincia elegida

                                # Buscamos la opción por texto (ej: "TORTUGUITAS")
                                texto_localidad = addr["locality"].upper().strip()
                                opcion_target_loc = driver.find_element(
                                    By.XPATH,
                                    f"//mat-option//span[contains(text(), '{texto_localidad}')]",
                                )
                                opcion_target_loc.click()
                                print(
                                    f"[Python Combo] Selección exitosa: {texto_localidad}"
                                )
                                time.sleep(1)
                            except Exception as e_loc:
                                print(
                                    f"[Python Combo] Error seleccionando localidad: {e_loc}"
                                )

                    # Datos de Matrícula (Verificá si el control se llama así, sino busca por placeholder)
                    if "college" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='colegio']"
                        ).send_keys(data["college"])
                    if "tome" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='tomo']"
                        ).send_keys(str(data["tome"]))
                    if "folio" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='folio']"
                        ).send_keys(str(data["folio"]))

                    # Contraseña Abogados
                    if "password" in data:
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='password']"
                        ).send_keys(data["password"])
                        driver.find_element(
                            By.CSS_SELECTOR, "input[formcontrolname='repPassword']"
                        ).send_keys(data["password"])

                # ==========================================
                # ESTRATEGIA B: REGISTRO DE TERCEROS
                # ==========================================
                else:
                    print(
                        "[Python] Detectada página de Terceros. Completando campos por ID..."
                    )
                    # Para terceros usamos los IDs exactos que me pasaste
                    if "name" in data:
                        driver.find_element(By.ID, "firstName").send_keys(data["name"])
                    if "surname" in data:
                        driver.find_element(By.ID, "lastName").send_keys(
                            data["surname"]
                        )
                    if "email" in data:
                        driver.find_element(By.ID, "email").send_keys(data["email"])
                        driver.find_element(By.ID, "repeatEmail").send_keys(
                            data["email"]
                        )
                    if "password" in data:
                        driver.find_element(By.ID, "password").send_keys(
                            data["password"]
                        )
                        driver.find_element(By.ID, "repeatPassword").send_keys(
                            data["password"]
                        )

            except Exception as e:
                print(
                    f"[Python Warning] Error al intentar rellenar un campo específico: {e}"
                )

            print("⚠️ [Python] Formulario listo. Por favor, resolvé el CAPTCHA...")

            # Tu bucle 'while not captcha_token' intacto abajo...
            captcha_token = ""
            while not captcha_token:
                try:
                    captcha_token = driver.execute_script(
                        'return document.getElementById("g-recaptcha-response").value;'
                    )
                    if not captcha_token:
                        captcha_token = driver.execute_script(
                            "return grecaptcha.getResponse();"
                        )
                except Exception:
                    pass
                time.sleep(1)

            return captcha_token

        finally:
            # Nos aseguramos de cerrar el navegador después de extraer el captcha para liberar memoria
            if self.driver:
                self.driver.quit()
                self.driver = None
