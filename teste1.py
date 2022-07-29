import requests
from bs4 import BeautifulSoup
import pandas as pd

lista_noticias = []

response = requests.get('https://archive.org/details/movies?query=tv&and[]=mediatype%3A%22movies%22')

content = response.content

site = BeautifulSoup(content, 'html.parser')

# HTML da notícia
noticias = site.findAll('div', attrs={'class': 'item-ia hov'})

for noticia in noticias:
  # Título
  titulo = noticia.find('a', attrs={'class': 'ttl'})

  # print(titulo.text)
  # print(titulo['href']) # link da notícia

  # Subtítulo: div class="feed-post-body-resumo"
  subtitulo = noticia.find('div', attrs={'class': 'by C C4'})

  if (subtitulo):
    # print(subtitulo.text)
    lista_noticias.append([titulo.text, subtitulo.text, titulo['href']])
  else:
    lista_noticias.append([titulo.text, '', titulo['href']])


news = pd.DataFrame(lista_noticias, columns=['Título', 'Subtítulo', 'Link'])

news.to_excel('noticias.xlsx', index=False)

# print(news)

