import requests
from bs4 import beautifulsoup


response = requests.get('https://vimeo.com/search/sort:latest?q=AULA')

content = response.content

site = BeautifulSoup(content, 'html.parser')

vídeo = site.find('a',attrs={'class': 'iris_video-vital__overlay iris_link-box iris_annotation-box iris_chip-box'})

print(vídeo)
