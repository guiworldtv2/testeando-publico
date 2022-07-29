import requests

response = requests.get('https://g1.globo.com')

print(response.content)
