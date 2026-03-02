from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time
import json
import logging
import re

# ===== CONFIGURACIÓN DE LOGS =====
logging.basicConfig(
    filename="Anid_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M"
)

def log_info(message):
    print(message)
    logging.info(message)


# ===== CONFIGURACIÓN DE CHROME =====
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)


# ===== FUNCIONES AUXILIARES =====
def limpiar_fecha(texto):
    match = re.search(r"(\d{1,2} de \w+, \d{4})|\d{4}", texto)
    return match.group(0) if match else "No disponible"


# ===== INICIO DEL SCRAPING =====
try:
    url = "https://anid.cl/concursos/"
    driver.get(url)
    log_info(f"Solicitando datos desde: {url}")
    time.sleep(6)

    def verificar_checkbox_abierto():
        """Activa el filtro 'Abierto' si no está seleccionado"""
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'jet-checkboxes-list__input')]")))
            checkbox = driver.find_element(By.XPATH, "//input[@class='jet-checkboxes-list__input' and @value='Abierto']")
            if not checkbox.is_selected():
                log_info("Activando checkbox 'Abierto'...")
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(5)
        except Exception as e:
            log_info(f"Error al verificar checkbox: {e}")

    verificar_checkbox_abierto()
    concursos_data = []

    def extraer_concursos():
        """Extrae los concursos visibles en la página actual"""
        try:
            concursos = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".elementor-element.elementor-element-e3dc4fd.e-flex.e-con-boxed.e-con.e-child")
            ))
            for concurso in concursos:
                try:
                    titulo = concurso.find_element(By.CSS_SELECTOR, "h3.elementor-heading-title").text.strip()
                    subdireccion = concurso.find_element(By.CSS_SELECTOR, "p.elementor-heading-title").text.strip()

                    fecha_inicio = "No disponible"
                    fecha_cierre = "No disponible"
                    fecha_fallo = "No disponible"

                    campos_dinamicos = concurso.find_elements(By.CLASS_NAME, "jet-listing-dynamic-field__content")
                    for campo in campos_dinamicos:
                        texto = campo.text.strip()
                        if texto.startswith("Inicio:"):
                            fecha_inicio = texto.replace("Inicio:", "").strip()
                        elif texto.startswith("Cierre:"):
                            fecha_cierre = texto.replace("Cierre:", "").strip()
                        elif texto.startswith("Fecha estimada de fallo:"):
                            partes = texto.split("Fecha estimada de fallo:")
                            fecha_fallo = partes[-1].strip() if len(partes) > 1 else "No disponible"

                    fecha_inicio = limpiar_fecha(fecha_inicio)
                    fecha_cierre = limpiar_fecha(fecha_cierre)

                    try:
                        enlace_ver_mas = concurso.find_element(By.CSS_SELECTOR, "a.elementor-button-link").get_attribute("href")
                    except NoSuchElementException:
                        enlace_ver_mas = "No disponible"

                    log_info(f"Concurso encontrado: {titulo}")
                    concursos_data.append({
                        "titulo": titulo,
                        "subdireccion": subdireccion,
                        "fecha_inicio": fecha_inicio,
                        "fecha_cierre": fecha_cierre,
                        "fecha_fallo": fecha_fallo,
                        "enlace_ver_mas": enlace_ver_mas
                    })
                except Exception as e:
                    log_info(f"Error procesando concurso individual: {e}")
        except Exception as e:
            log_info(f"Error al extraer concursos: {e}")


    # --- Primera página ---
    extraer_concursos()
    current_page = 1

    # --- PAGINACIÓN ESTABLE ---
    while True:
        try:
            paginacion_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jet-filters-pagination")))
            paginas = paginacion_div.find_elements(By.CLASS_NAME, "jet-filters-pagination__item")

            boton_siguiente = None
            for pagina in paginas:
                if pagina.get_attribute("data-value") == "next":
                    boton_siguiente = pagina
                    break

            if not boton_siguiente:
                log_info("No hay más páginas.")
                break

            log_info(f"Avanzando a la página {current_page + 1}...")
            verificar_checkbox_abierto()

            concursos_actuales = driver.find_elements(
                By.CSS_SELECTOR, ".elementor-element.elementor-element-e3dc4fd.e-flex.e-con-boxed.e-con.e-child"
            )
            ultimo_concurso = concursos_actuales[-1].text.strip() if concursos_actuales else ""

            # Hacer clic en “Siguiente”
            driver.execute_script("arguments[0].click();", boton_siguiente)

            # Espera adicional fija para permitir carga de la página
            log_info("Esperando 7 segundos para cargar nuevos concursos...")
            time.sleep(7)

            # Verificar que haya nuevos elementos
            nuevos_concursos = driver.find_elements(
                By.CSS_SELECTOR, ".elementor-element.elementor-element-e3dc4fd.e-flex.e-con-boxed.e.con.e.child"
            )

            if not nuevos_concursos:
                log_info("No se detectaron nuevos concursos, intentando esperar más...")
                time.sleep(5)

            extraer_concursos()
            current_page += 1

        except Exception as e:
            log_info(f"Error en la paginación: {e}")
            break

finally:
    driver.quit()
    log_info("Proceso finalizado.")
    with open("fondos_anid.json", "w", encoding="utf-8") as f:
        json.dump(concursos_data, f, ensure_ascii=False, indent=4)
    log_info("Datos guardados exitosamente en fondos_anid.json.")
