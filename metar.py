import requests

url = "https://weatherapi-com.p.rapidapi.com/alerts.json"

querystring = {"q":"london"}

headers = {"x-rapidapi-host": "weatherapi-com.p.rapidapi.com"}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
