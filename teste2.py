import requests

response = requests.get('https://vimeo.com/search/sort:latest?q=AULA')

print(response.content)
