import requests
import json
from datetime import datetime

# --- Configuración ---
# Tu clave API de AEMET (por seguridad, en entornos productivos se recomienda no incluirla en texto plano)
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsdWRvdmljay5nYXJjaWFAZ21haWwuY29tIiwianRpIjoiMDAzMTNiOGYtNTJmNS00NjE1LTlhZWQtZmI3ZmVkYWE2NWVmIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NDQ1MzkyMTQsInVzZXJJZCI6IjAwMzEzYjhmLTUyZjUtNDYxNS05YWVkLWZiN2ZlZGFhNjVlZiIsInJvbGUiOiIifQ.4ou1l_ZWTMwXt41ukxHp8RAuxzPXIx0QCQdehPTNgzo"
# Código del aeropuerto
ESTACION = "GCLP"
# URL base para la predicción específica de aeropuertos según la documentación de AEMET:
BASE_URL = f"https://opendata.aemet.es/opendata/api/prediccion/especifica/aeropuerto/{ESTACION}?api_key={API_KEY}"

def fetch_data():
    """
    Hace la primera petición para obtener la URL de los datos detallados,
    y luego descarga el contenido JSON de la predicción.
    """
    # Primera petición a la API de AEMET.
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        raise Exception(f"Error al obtener los datos (código {response.status_code})")

    response_json = response.json()

    # La respuesta contiene una clave "datos" que tiene la URL con el JSON real.
    datos_url = response_json.get('datos')
    if not datos_url:
        raise Exception("No se encontró la URL de datos en la respuesta de AEMET.")

    # Segunda petición para obtener el JSON con la predicción.
    detailed_response = requests.get(datos_url)
    if detailed_response.status_code != 200:
        raise Exception(f"Error al obtener los datos detallados (código {detailed_response.status_code})")

    return detailed_response.json()

def extract_weather_for_wednesday(data):
    """
    Dado el JSON con la predicción, busca la información correspondiente al miércoles
    y extrae los siguientes parámetros:
      - Visibilidad
      - Techo de nubes
      - Vientos
      - Lluvia
      - Temperatura

    Se asume que la estructura de 'data' tiene una clave "prediccion"
    que a su vez contiene una lista "dia" con la información diaria.
    """
    # Verifica que la estructura contenga la clave "prediccion" y luego "dia"
    prediccion = data.get("prediccion")
    if not prediccion:
        raise Exception("La respuesta no contiene la clave 'prediccion'.")
    
    dias = prediccion.get("dia")
    if not dias:
        raise Exception("La respuesta no contiene información diaria en 'dia'.")

    # Buscar el día que corresponde a miércoles.
    wednesday_data = None
    for dia in dias:
        fecha_str = dia.get("fecha")
        if not fecha_str:
            continue
        try:
            # Convertir la fecha al objeto datetime (se asume formato "YYYY-MM-DD")
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        except Exception as e:
            continue
        # datetime.weekday(): lunes=0, martes=1, miércoles=2, etc.
        if fecha.weekday() == 2:
            wednesday_data = dia
            break

    if not wednesday_data:
        raise Exception("No se encontraron datos para el miércoles.")

    # Extraer los parámetros solicitados.
    # Es posible que los nombres de los campos varíen:
    visibilidad = wednesday_data.get("visibilidad", "No disponible")
    techo_nubes = wednesday_data.get("techo_nubes", "No disponible")
    vientos = wednesday_data.get("viento", "No disponible")
    lluvia = wednesday_data.get("lluvia", "No disponible")
    temperatura = wednesday_data.get("temperatura", "No disponible")
    
    return {
        "fecha": wednesday_data.get("fecha"),
        "visibilidad": visibilidad,
        "techo_nubes": techo_nubes,
        "vientos": vientos,
        "lluvia": lluvia,
        "temperatura": temperatura
    }

def main():
    try:
        # Obtención de datos desde AEMET.
        data = fetch_data()
        # Extracción de los datos meteorológicos para el miércoles.
        weather = extract_weather_for_wednesday(data)
        print("Datos meteorológicos para el aeropuerto GCLP (miércoles):")
        print("-" * 50)
        print(f"Fecha:         {weather.get('fecha')}")
        print(f"Visibilidad:   {weather.get('visibilidad')}")
        print(f"Techo de nubes:{weather.get('techo_nubes')}")
        print(f"Vientos:       {weather.get('vientos')}")
        print(f"Lluvia:        {weather.get('lluvia')}")
        print(f"Temperatura:   {weather.get('temperatura')}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
