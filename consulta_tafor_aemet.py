
import requests

# Parámetros
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsdWRvdmljay5nYXJjaWFAZ21haWwuY29tIiwianRpIjoiMDAzMTNiOGYtNTJmNS00NjE1LTlhZWQtZmI3ZmVkYWE2NWVmIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NDQ1MzkyMTQsInVzZXJJZCI6IjAwMzEzYjhmLTUyZjUtNDYxNS05YWVkLWZiN2ZlZGFhNjVlZiIsInJvbGUiOiIifQ.4ou1l_ZWTMwXt41ukxHp8RAuxzPXIx0QCQdehPTNgzo"
ICAO = "GCLP"  # Gran Canaria por defecto

# URL para METAR/TAFOR
endpoint = f"https://opendata.aemet.es/opendata/api/aviacion/tafore/?api_key={API_KEY}"

# Paso 1: solicitar el recurso
res = requests.get(endpoint)
if res.status_code != 200:
    raise Exception(f"Error al solicitar TAFOR: {res.status_code} - {res.text}")

datos = res.json()
# Paso 2: acceder al recurso real
taf_url = datos['datos']
taf_res = requests.get(taf_url)
taf_data = taf_res.json()

# Filtrar por ICAO
taf_actual = next((item for item in taf_data if item["icao"] == ICAO), None)

if taf_actual:
    print(f"TAFOR para {ICAO}:")
    print(taf_actual["taf"])
else:
    print(f"No se encontró TAFOR para {ICAO}")
