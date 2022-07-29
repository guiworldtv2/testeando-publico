import requests
from bs4 import BeautifulSoup
import pandas as pd

lista_noticias = []

response = requests.get('https://www.youtube.com/results?search_query=aula&sp=CAISBBABGAI%253D')

content = response.content

site = BeautifulSoup(content, 'html.parser')

# HTML da notícia
noticias = site.findAll('div', attrs= {'id': 'dismissible'},{'class': 'style-scope ytd-video-renderer'})

for noticia in noticias:
  # Título
  titulo = noticia.find('a', attrs= {'id': 'dismissible'},{'class': 'style-scope ytd-video-renderer'})

  # print(titulo.text)
  # print(titulo['href']) # link da notícia

  # Subtítulo: div class="feed-post-body-resumo"
  subtitulo = noticia.find('span', attrs={'class': 'style-scope yt-formatted-string'})

  if (subtitulo):
    # print(subtitulo.text)
    lista_noticias.append([titulo.text, subtitulo.text, titulo['href']])
  else:
    lista_noticias.append([titulo.text, '', titulo['href']])


news = pd.DataFrame(lista_noticias, columns=['Título', 'Subtítulo', 'Link'])

news.to_excel('noticias.xlsx', index=False)

# print(news)

