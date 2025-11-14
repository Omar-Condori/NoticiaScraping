import requests
from bs4 import BeautifulSoup

url = "https://rpp.pe"
response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'html.parser')

# Buscar diferentes elementos comunes
print("=== ARTÍCULOS ===")
print(f"<article>: {len(soup.find_all('article'))}")
print(f"<div class='story'>: {len(soup.find_all('div', class_='story'))}")
print(f"<div class='noticia'>: {len(soup.find_all('div', class_='noticia'))}")

print("\n=== TÍTULOS ===")
print(f"<h1>: {len(soup.find_all('h1'))}")
print(f"<h2>: {len(soup.find_all('h2'))}")
print(f"<h3>: {len(soup.find_all('h3'))}")

print("\n=== PRIMER ARTÍCULO ===")
primer_articulo = soup.find('article') or soup.find('div', class_='story')
if primer_articulo:
    print(primer_articulo.prettify()[:500])