
import requests

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsdWRvdmljay5nYXJjaWFAZ21haWwuY29tIiwianRpIjoiMDAzMTNiOGYtNTJmNS00NjE1LTlhZWQtZmI3ZmVkYWE2NWVmIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NDQ1MzkyMTQsInVzZXJJZCI6IjAwMzEzYjhmLTUyZjUtNDYxNS05YWVkLWZiN2ZlZGFhNjVlZiIsInJvbGUiOiIifQ.4ou1l_ZWTMwXt41ukxHp8RAuxzPXIx0QCQdehPTNgzo"
endpoint = f"https://opendata.aemet.es/opendata/api/aviacion/tafore/?api_key={API_KEY}"

print("🔍 Conectando con AEMET...")
response = requests.get(endpoint)

print(f"✅ Código de estado: {response.status_code}")
print("📦 Respuesta completa:")
print(response.text)
