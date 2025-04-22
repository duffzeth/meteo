import requests
import json

url = "https://api.checkwx.com/metar/KJFK/decoded"

response = requests.request("GET", url, headers={'X-API-Key': 'aafbb320264a4b3eacbc2fd57549fe76'})

print(response.text)
