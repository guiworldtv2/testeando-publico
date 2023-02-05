import requests
from bs4 import BeautifulSoup
import pandas as pd

lista_noticias = []

response = requests.get('https://g1.globo.com/')

content = response.content

site = BeautifulSoup(content, 'html.parser')

# HTML da notícia
noticias = site.findAll('div', attrs={'class': 'feed-post-body'})

for noticia in noticias:
  # Título
  titulo = noticia.find('a', attrs={'class': 'feed-post-link'})

  # print(titulo.text)
  # print(titulo['href']) # link da notícia

  # Subtítulo: div class="feed-post-body-resumo"
  subtitulo = noticia.find('div', attrs={'class': 'feed-post-body-resumo'})

  if (subtitulo):
    # print(subtitulo.text)
    lista_noticias.append([titulo.text, subtitulo.text, titulo['href']])
  else:
    lista_noticias.append([titulo.text, '', titulo['href']])


news = pd.DataFrame(lista_noticias, columns=['Título', 'Subtítulo', 'Link'])

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def dataframe_to_pdf(dataframe, file_path):
    pdf_pages = canvas.Canvas(file_path, pagesize=letter)

    max_rows_per_page = 47
    page_number = 1
    page_count = (len(dataframe) // max_rows_per_page) + 1

    for i in range(0, page_count):
        pdf_pages.drawString(72, 720, "Page " + str(page_number))
        pdf_pages.drawString(72, 700, "Título")
        pdf_pages.drawString(72 + 150, 700, "Subtítulo")
        pdf_pages.drawString(72 + 300, 700, "Link")

        for j in range(0, max_rows_per_page):
            if (i * max_rows_per_page + j >= len(dataframe)):
                break

            row = dataframe.iloc[i * max_rows_per_page + j]
            pdf_pages.drawString(72, 680 - 20 * j, row['Título'])
            pdf_pages.drawString(72 + 150, 680 - 20 * j, row['Subtítulo'])
            pdf_pages.drawString(72 + 300, 680 - 20 * j, row['Link'])

        pdf_pages.showPage()
        page_number += 1

    pdf_pages.save()

dataframe_to_pdf(news, 'noticias.pdf')


news.to_pdf('noticias.pdf', index=False)


# print(news)
