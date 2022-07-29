import requests
from bs4 import beautifulsoup


response = requests.get('https://vimeo.com/search/sort:latest?q=AULA')

content = response.content

site = BeautifulSoup(content, 'html.parser')

vídeo = site.find('div',attrs={'class': 'iris_p_infinite__item span-1'})

print(vídeo)
