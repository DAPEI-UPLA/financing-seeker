import os
import httpx
import json
from datetime import date
import time

def google_search(api_key, search_engine_id, query, **params):
    base_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'dateRestrict': 'w1',
        **params
    }
    response = httpx.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

search_engine_id = '219ebe172fe8a485e'
queries = ['Fondos concursable', 'Concurso', 'Llamado', 'Postulaciones', 'Iniciativas', 'Lanzamientos', 'Fondo Nacional', 'Fondo de fomento', 'Desafío', 'Convocatoria']

search_results = []
fecha_actual = date.today().strftime("%d-%m-%Y")

for query in queries:
    print(f"Buscando: {query}")
    for start_index in range(1, 100, 10): 
        try:
            response = google_search(
                api_key=api_key,
                search_engine_id=search_engine_id,
                query=query,
                start=start_index
            )
            for item in response.get('items', []):
                search_results.append({
                    "consulta": query,
                    "titulo": item.get("title"),
                    "link": item.get("link"),
                    "sitio": item.get("displayLink"),
                    "fecha de busqueda": fecha_actual
                })
            time.sleep(1)  
        except Exception as e:
            print(f"Error en la búsqueda '{query}' desde {start_index}: {e}")
            continue


nombre_archivo = f'google_search_results.json'
with open(nombre_archivo, 'w', encoding='utf-8') as f:
    json.dump(search_results, f, ensure_ascii=False, indent=2)
