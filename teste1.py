import requests
from bs4 import BeautifulSoup
import pandas as pd

lista_noticias = []

response = requests.get('https://archive.org/details/movies?query=tv&and[]=mediatype%3A%22movies%22')

content = response.content

site = BeautifulSoup(content, 'html.parser')

# HTML da notícia
noticias = site.findAll('div', attrs={'class': 'item-ia hov'})

# Título

titulo = noticia.find('a', attrs={'class':'item-ia hov'})

print(titulo)
