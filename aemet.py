import http.client

conn = http.client.HTTPSConnection("opendata.aemet.es")

headers = {
    'cache-control': "no-cache"
    }

conn.request("GET", "/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/?api_key=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsdWRvdmljay5nYXJjaWFAZ21haWwuY29tIiwianRpIjoiMDAzMTNiOGYtNTJmNS00NjE1LTlhZWQtZmI3ZmVkYWE2NWVmIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NDQ1MzkyMTQsInVzZXJJZCI6IjAwMzEzYjhmLTUyZjUtNDYxNS05YWVkLWZiN2ZlZGFhNjVlZiIsInJvbGUiOiIifQ.4ou1l_ZWTMwXt41ukxHp8RAuxzPXIx0QCQdehPTNgzo", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
