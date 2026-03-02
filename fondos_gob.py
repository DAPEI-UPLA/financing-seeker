#!/usr/bin/env python
# coding: utf-8

# # Fondos.gob.cl

# In[1]:


import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime


class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return datetime.fromtimestamp(record.created).strftime("%H:%M")



formatter = CustomFormatter('%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("scraping_fondos_gob.log"),
        logging.StreamHandler()
    ]
)



for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)

def obtener_fondos():
    url = "https://fondos.gob.cl/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    logs = [
        "-" * 40,
        f"Solicitando datos desde: {url}",
    ]
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            logs.append("Conexión exitosa a la página.")
            soup = BeautifulSoup(response.text, "html.parser")
            fondos = soup.find_all("div", class_="col-md-6 col-lg-3")
            
            datos_fondos = []
            for fondo in fondos:
                nombre_tag = fondo.find("h6", class_="mt-1")
                estado_tag = fondo.find("span", class_="badge bg-green rounded-pill")
                ubicacion_tag = fondo.find("span", class_="text-white")
                origen_tag = fondo.find("small", class_="text-uppercase text-rosa")
                link_tag = fondo.find("a", href=True)
                beneficiarios_tag = fondo.find("p")

                beneficiarios = beneficiarios_tag.text.strip() if beneficiarios_tag else "No especificado"
                
                fechas = "No especificado"
                fechas_p_tag = fondo.find_all("p")
                for p in fechas_p_tag:
                    if "Inicio:" in p.text and "Fin:" in p.text:
                        fechas = p.text.strip().replace("|", " ").replace("Inicio:", "Inicio: ").replace("Fin:", " Fin: ")
                        break
                
                montos = "No especificado"
                for p in fechas_p_tag:
                    if p.find_previous("b") and "Montos:" in p.find_previous("b").text:
                        montos = p.text.strip()
                        break
                
                if nombre_tag and estado_tag and ubicacion_tag and origen_tag and link_tag:
                    datos_fondos.append({
                        "nombre": nombre_tag.text.strip(),
                        "estado": estado_tag.text.strip(),
                        "ubicacion": ubicacion_tag.text.strip(),
                        "origen": origen_tag.text.strip(),
                        "link": "https://fondos.gob.cl" + link_tag["href"],
                        "beneficiarios": beneficiarios,
                        "fechas": fechas,
                        "montos": montos
                    })
            
            logs.append(f"Se han obtenido {len(datos_fondos)} fondos.")
        else:
            logs.append(f"Error al acceder a la página. Código de estado: {response.status_code}")
            return [], logs

        logs.append("Proceso finalizado.")
        return datos_fondos, logs

    except Exception as e:
        logs.append(f"Error durante la solicitud HTTP: {e}")
        return [], logs

def guardar_json(datos, logs, archivo="fondos_gob.json"):
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        logs.append(f"Datos guardados exitosamente en {archivo}.")
    except Exception as e:
        logs.append(f"Error al guardar los datos en JSON: {e}")



    logs.append("-" * 40)

    
    logging.info("\n".join(logs))

if __name__ == "__main__":
    fondos, logs = obtener_fondos()
    
    if fondos:
        guardar_json(fondos, logs)
        
        for fondo in fondos:
            print("-------------------")
            print(f"Nombre: {fondo['nombre']}")
            print(f"Estado: {fondo['estado']}")
            print(f"Ubicación: {fondo['ubicacion']}")
            print(f"Origen: {fondo['origen']}")
            print(f"Link: {fondo['link']}")
            print(f"Beneficiarios: {fondo['beneficiarios']}")
            print(f"Fechas: {fondo['fechas']}")
            print(f"Montos: {fondo['montos']}")
            print("-------------------")


# In[ ]:




