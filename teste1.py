import requests
from bs4 import BeautifulSoup
import pandas as pd

lista_noticias = []

response = requests.get('https://vimeo.com/search/sort:latest?q=AULA/')

content = response.content

site = BeautifulSoup(content, 'html.parser')

# HTML da notícia
noticias = site.findAll('a', attrs={'class': 'iris_video-vital__overlay iris_link-box iris_annotation-box iris_chip-box'})

for noticia in noticias:
  # Título
  titulo = noticia.find('div', attrs={'class': 'iris_video-vital__title'})

  # print(titulo.text)
  # print(titulo['href']) # link da notícia

  # Subtítulo: div class="feed-post-body-resumo"
  subtitulo = noticia.find('div', attrs={'class': 'iris_attribution_panel iris_attribution_panel--browse l-text-left'})

  if (subtitulo):
    # print(subtitulo.text)
    lista_noticias.append([titulo.text, subtitulo.text, titulo['href']])
  else:
    lista_noticias.append([titulo.text, '', titulo['href']])


news = pd.DataFrame(lista_noticias, columns=['Título', 'Subtítulo', 'Link'])

news.to_excel('noticias.xlsx', index=False)

# print(news)
