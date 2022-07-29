import requests

response = requests.get('https://vimeo.com/search/sort:latest?q=AULA')

print('Status code:', response.status_code)

print('↓↓Header↓↓')
print(response.headers)

print('\n↓↓Content↓↓')
print(response.content)
