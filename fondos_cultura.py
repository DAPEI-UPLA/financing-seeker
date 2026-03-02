#!/usr/bin/env python
# coding: utf-8

# # Pagina https://www.fondosdecultura.cl/area/

# In[1]:


import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging

logging.basicConfig(
    filename="fondos_cultura_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_info(message):
    """Función para registrar mensajes informativos."""
    print(message)
    logging.info(message)

def log_error(message):
    """Función para registrar mensajes de error."""
    print(f" {message}")
    logging.error(message)


urls = [
    "arquitectura", "artes-visuales", "artes-escenicas", "artesania", "audiovisual", "circo", "evaluadores",
    "danza", "diseno", "economia-creativa", "educacion", "folclor", "formacion-residencias", "fotografia",
    "gestion-cultural", "infraestructura", "interdisciplinas", "libro-lectura", "micsur", "musica",
    "narracion-oral", "nuevos-medios", "opera", "organizaciones", "patrimonio", "pueblos-originarios",
    "regiones", "teatro", "titeres", "turismo-cultural"
]

url_base = "https://www.fondosdecultura.cl/area/{}/"

def guardar_en_json(datos, archivo="fondos_cultura.json"):
    """Guarda los datos en un archivo JSON."""
    try:
      
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                data_existente = json.load(f)
        except FileNotFoundError:
            data_existente = []

        data_existente.extend(datos)

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data_existente, f, ensure_ascii=False, indent=4)

        log_info(f"Datos guardados exitosamente en {archivo}")
    except Exception as e:
        log_error(f"Error al guardar en JSON: {e}")

def obtener_convocatoria():
    convocatorias_abiertas = []  

    for categoria in urls:
        url = url_base.format(categoria)

        try:
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()  

            soup = BeautifulSoup(response.text, "html.parser")

            convocatorias = soup.find_all("div", class_="col-md-4")
            if not convocatorias:
                log_info(f"Página {url} sin convocatorias")
                continue

            hay_convocatorias_abiertas = False

            for convocatoria in convocatorias:
                try:
                   
                    titulo = convocatoria.find("h5", class_="card-title").text.strip()

                    link = convocatoria.find("a")["href"]

                    fecha_texto = convocatoria.find("p", class_="card-text").text.strip()

                    if "Fecha de cierre:" in fecha_texto:
                        
                        fecha_cierre_str = fecha_texto.replace("Fecha de cierre:", "").strip()
                        try:
                           
                            fecha_cierre = datetime.strptime(fecha_cierre_str, "%d/%m/%Y - %H:%M")
                            hoy = datetime.now()

                            if fecha_cierre > hoy:
                                hay_convocatorias_abiertas = True

                                convocatoria_data = {
                                    "categoria": categoria,
                                    "titulo": titulo,
                                    "enlace": link,
                                    "fecha_cierre": fecha_cierre_str
                                }

                                convocatorias_abiertas.append(convocatoria_data)

                                log_info(f" Convocatoria ABIERTA encontrada:")
                                log_info(f" Enlace: {link}")
                                log_info(f" Título: {titulo}")
                                log_info(f" Fecha de cierre: {fecha_cierre_str}")
                                log_info("-" * 40)

                        except ValueError:
                            
                            log_error(f"Formato de fecha inválido: {fecha_cierre_str}")
                            continue

                except Exception as e:
                    log_error(f"Error al procesar una convocatoria en {url}: {e}")

            if not hay_convocatorias_abiertas:
                log_info(f"Página {url} sin convocatorias abiertas")

        except requests.exceptions.HTTPError as http_err:
            log_error(f"Error HTTP al acceder a {url}: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            log_error(f"Error de conexión al acceder a {url}: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            log_error(f"Tiempo de espera agotado al acceder a {url}: {timeout_err}")
        except Exception as e:
            log_error(f"Error inesperado al acceder a {url}: {e}")

    if convocatorias_abiertas:
        guardar_en_json(convocatorias_abiertas)

if __name__ == "__main__":
    obtener_convocatoria()


# In[ ]:




