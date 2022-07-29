import requests

response = requests.get('https://vimeo.com/search/sort:latest?q=AULA')

print('Status code:', response.status_code)

print('↓↓Header↓↓')

print('\n↓↓Content↓↓')
print(response.content)
