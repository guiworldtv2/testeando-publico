import requests
from bs4 import BeautifulSoup
import pandas as pd

lista_noticias = []

response = requests.get('https://www.r7.com/')

content = response.content

site = BeautifulSoup(content, 'html.parser')

# HTML da notícia
noticias = site.findAll('div', attrs={'class': 'r7-flex-hat'})

for noticia in noticias:
  # Título
  titulo = noticia.find('a', attrs={'class': 'r7-flex-title-h1'})

  # print(titulo.text)
  # print(titulo['href']) # link da notícia

  # Subtítulo: div class="feed-post-body-resumo"
  subtitulo = noticia.find('div', attrs={'class': 'r7-flex-hat'})

  if (subtitulo):
    # print(subtitulo.text)
    lista_noticias.append([titulo.text, subtitulo.text, titulo['href']])
  else:
    lista_noticias.append([titulo.text, '', titulo['href']])


news = pd.DataFrame(lista_noticias, columns=['Título', 'Subtítulo', 'Link'])

news.to_excel('noticias.xlsx', index=False)

# print(news)
