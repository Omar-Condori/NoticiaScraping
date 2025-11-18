import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from database import Database

class NewsScraper:
    def __init__(self):
        """Inicializa el scraper con la base de datos"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.db = Database()
        
        # Crear tablas si no existen
        print("📊 Verificando base de datos...")
        self.db.crear_tablas()
        
        # Nota: Ya no agregamos fuentes de ejemplo automáticamente
        # Cada usuario debe agregar sus propias fuentes
    
    def _agregar_fuentes_ejemplo(self):
        """Agrega fuentes de noticias de ejemplo"""
        fuentes_ejemplo = [
            {
                'nombre': 'BBC News',
                'url': 'https://www.bbc.com/news',
                'selector_contenedor': {'name': 'div', 'attrs': {'data-testid': 'card-text-wrapper'}},
                'selector_titulo': {'name': 'h2'},
                'selector_resumen': {'name': 'p'},
                'selector_link': {'name': 'a'},
                'selector_imagen': {'name': 'img'},
                'selector_categoria': {'name': 'span', 'attrs': {'class': 'category'}},
                'activo': True
            },
            {
                'nombre': 'CNN',
                'url': 'https://edition.cnn.com',
                'selector_contenedor': {'name': 'div', 'attrs': {'class': 'container__item'}},
                'selector_titulo': {'name': 'span', 'attrs': {'class': 'container__headline-text'}},
                'selector_resumen': {'name': 'div', 'attrs': {'class': 'container__description'}},
                'selector_link': {'name': 'a'},
                'selector_imagen': {'name': 'img'},
                'selector_categoria': None,
                'activo': True
            }
        ]
        
        for fuente in fuentes_ejemplo:
            self.db.agregar_fuente(fuente)
    
    # ==================== GESTIÓN DE FUENTES ====================
    
    def agregar_fuente(self, fuente: Dict, user_id: int) -> Optional[Dict]:
        """Agrega una nueva fuente (asociada a un usuario)"""
        return self.db.agregar_fuente(fuente, user_id)
    
    def obtener_fuentes(self, solo_activas: bool = False, user_id: Optional[int] = None, es_admin: bool = False) -> List[Dict]:
        """Obtiene fuentes (filtradas por usuario si no es admin)"""
        return self.db.obtener_fuentes(solo_activas, user_id, es_admin)
    
    def obtener_fuente(self, fuente_id: int, user_id: Optional[int] = None, es_admin: bool = False) -> Optional[Dict]:
        """Obtiene una fuente por ID (verifica que pertenezca al usuario si no es admin)"""
        return self.db.obtener_fuente(fuente_id, user_id, es_admin)
    
    def actualizar_fuente(self, fuente_id: int, datos: Dict, user_id: Optional[int] = None, es_admin: bool = False) -> Optional[Dict]:
        """Actualiza una fuente (verifica que pertenezca al usuario si no es admin)"""
        return self.db.actualizar_fuente(fuente_id, datos, user_id, es_admin)
    
    def eliminar_fuente(self, fuente_id: int, user_id: Optional[int] = None, es_admin: bool = False) -> bool:
        """Elimina una fuente (verifica que pertenezca al usuario si no es admin)"""
        return self.db.eliminar_fuente(fuente_id, user_id, es_admin)
    
    # ==================== SCRAPING PROFUNDO ====================
    
    def _scrapear_pagina_individual(self, url: str, titulo_parcial: str = None) -> Dict:
        """
        Hace scraping profundo de una página individual de noticia
        Retorna un dict con titulo, resumen, imagen_url, fecha_publicacion
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            resultado = {
                'titulo': None,
                'resumen': None,
                'imagen_url': None,
                'fecha_publicacion': None
            }
            
            # ========== EXTRAER TÍTULO ==========
            # Estrategia 1: Meta tags (más confiable)
            for meta_tag in soup.find_all('meta'):
                property_attr = meta_tag.get('property', '') or meta_tag.get('name', '')
                if 'og:title' in property_attr.lower() or 'twitter:title' in property_attr.lower():
                    resultado['titulo'] = meta_tag.get('content', '').strip()
                    break
            
            # Estrategia 2: h1 principal
            if not resultado['titulo']:
                h1_tags = soup.find_all('h1')
                for h1 in h1_tags:
                    h1_text = h1.get_text(strip=True)
                    if h1_text and len(h1_text) > 10:
                        resultado['titulo'] = h1_text
                        break
            
            # Estrategia 3: title tag
            if not resultado['titulo']:
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text(strip=True)
                    # Limpiar títulos que incluyen el nombre del sitio
                    if '|' in title_text:
                        title_text = title_text.split('|')[0].strip()
                    if '-' in title_text and len(title_text.split('-')) > 2:
                        title_text = title_text.split('-')[0].strip()
                    if title_text and len(title_text) > 10:
                        resultado['titulo'] = title_text
            
            # Estrategia 4: Usar título parcial si existe
            if not resultado['titulo'] and titulo_parcial:
                resultado['titulo'] = titulo_parcial
            
            # ========== EXTRAER IMAGEN ==========
            # Estrategia 1: Meta tags (más confiable)
            for meta_tag in soup.find_all('meta'):
                property_attr = meta_tag.get('property', '') or meta_tag.get('name', '')
                if 'og:image' in property_attr.lower() or 'twitter:image' in property_attr.lower():
                    img_url = meta_tag.get('content', '').strip()
                    if img_url and not img_url.startswith('data:'):
                        resultado['imagen_url'] = urljoin(url, img_url)
                        break
            
            # Estrategia 2: Buscar imagen principal con clases comunes
            if not resultado['imagen_url']:
                for class_pattern in ['featured-image', 'main-image', 'article-image', 'post-image', 'hero-image', 'principal']:
                    img_elem = soup.find('img', attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                    if img_elem:
                        img_url = (img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src'))
                        if img_url and not img_url.startswith('data:'):
                            resultado['imagen_url'] = urljoin(url, img_url)
                            break
            
            # Estrategia 3: Primera imagen grande en el contenido
            if not resultado['imagen_url']:
                article_content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content|article|post'))
                if article_content:
                    imgs = article_content.find_all('img', limit=5)
                    for img in imgs:
                        img_url = (img.get('src') or img.get('data-src') or img.get('data-lazy-src'))
                        if img_url and not img_url.startswith('data:'):
                            # Filtrar iconos
                            if not any(icon in img_url.lower() for icon in ['icon', 'logo', 'avatar', 'favicon']):
                                resultado['imagen_url'] = urljoin(url, img_url)
                                break
            
            # ========== EXTRAER RESUMEN/DESCRIPCIÓN ==========
            # Estrategia 1: Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc:
                desc = meta_desc.get('content', '').strip()
                if desc and len(desc) > 20:
                    resultado['resumen'] = desc[:500]
            
            # Estrategia 2: Primer párrafo del artículo
            if not resultado['resumen'] or len(resultado['resumen']) < 20:
                article_content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content|article|post|entry'))
                if article_content:
                    paragraphs = article_content.find_all('p')
                    for p in paragraphs:
                        p_text = p.get_text(strip=True)
                        # Filtrar párrafos que son metadata (fechas, autores, etc.)
                        if len(p_text) > 50 and len(p_text) < 1000:
                            # Evitar párrafos que parecen metadata
                            if not any(word in p_text.lower() for word in ['por ', 'publicado', 'actualizado', 'fecha:', 'hora:']):
                                resultado['resumen'] = p_text[:500]
                                break
                    
                    # Si aún no hay resumen, buscar en divs con clases específicas
                    if not resultado['resumen'] or len(resultado['resumen']) < 20:
                        for class_pattern in ['lead', 'intro', 'summary', 'excerpt', 'abstract', 'preview', 'description']:
                            desc_div = article_content.find('div', attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                            if desc_div:
                                desc_text = desc_div.get_text(strip=True)
                                if len(desc_text) > 30:
                                    resultado['resumen'] = desc_text[:500]
                                    break
            
            # ========== EXTRAER FECHA DE PUBLICACIÓN ==========
            # Estrategia 1: Meta tags
            for meta_tag in soup.find_all('meta'):
                property_attr = meta_tag.get('property', '') or meta_tag.get('name', '')
                if 'published_time' in property_attr.lower() or 'article:published_time' in property_attr.lower():
                    fecha_str = meta_tag.get('content', '').strip()
                    if fecha_str:
                        try:
                            resultado['fecha_publicacion'] = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                        except:
                            pass
                    break
            
            # Estrategia 2: time tag con datetime
            time_tag = soup.find('time', attrs={'datetime': True})
            if time_tag and not resultado['fecha_publicacion']:
                fecha_str = time_tag.get('datetime', '').strip()
                if fecha_str:
                    try:
                        resultado['fecha_publicacion'] = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    except:
                        pass
            
            # Estrategia 3: Buscar en elementos con clases de fecha
            if not resultado['fecha_publicacion']:
                for class_pattern in ['date', 'fecha', 'published', 'pub-date', 'time', 'timestamp']:
                    date_elem = soup.find(attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        # Intentar parsear diferentes formatos de fecha
                        fecha_parseada = self._parsear_fecha(date_text)
                        if fecha_parseada:
                            resultado['fecha_publicacion'] = fecha_parseada
                            break
            
            return resultado
            
        except Exception as e:
            print(f"      ⚠️ Error en scraping profundo de {url}: {e}")
            return {
                'titulo': None,
                'resumen': None,
                'imagen_url': None,
                'fecha_publicacion': None
            }
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """Intenta parsear diferentes formatos de fecha"""
        if not fecha_str:
            return None
        
        # Formatos comunes
        formatos = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%d/%m/%Y %H:%M',
            '%d-%m-%Y %H:%M',
            '%Y-%m-%d',
            '%d/%m/%Y',
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str.strip(), formato)
            except:
                continue
        
        return None
    
    # ==================== SCRAPING ====================
    
    def scrape_fuente(self, fuente: Dict, limite: int = 5, guardar: bool = True, user_id: Optional[int] = None) -> List[Dict]:
        """Scrapea noticias de una fuente específica"""
        # Guardar user_id temporalmente para usar en guardar_noticia
        self._current_user_id = user_id
        noticias = []
        
        print(f"🔍 Scrapeando: {fuente['nombre']}")
        
        try:
            response = requests.get(fuente['url'], headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            contenedor = fuente['selector_contenedor']
            
            # Intentar encontrar artículos con el selector configurado
            articulos = soup.find_all(
                contenedor['name'],
                contenedor.get('attrs', {}),
                limit=limite
            )
            
            # Si no se encontraron artículos, intentar selectores alternativos comunes
            if len(articulos) == 0:
                print(f"   ⚠️ No se encontraron artículos con el selector configurado, intentando alternativas...")
                # Intentar selectores alternativos comunes
                selectores_alternativos = [
                    {'name': 'article'},
                    {'name': 'div', 'attrs': {'class': re.compile('article|story|news|noticia|post', re.I)}},
                    {'name': 'div', 'attrs': {'itemtype': 'http://schema.org/NewsArticle'}},
                    {'name': 'div', 'attrs': {'data-testid': re.compile('article|story', re.I)}},
                ]
                
                for selector_alt in selectores_alternativos:
                    articulos = soup.find_all(
                        selector_alt['name'],
                        selector_alt.get('attrs', {}),
                        limit=limite
                    )
                    if len(articulos) > 0:
                        print(f"   ✓ Encontrados {len(articulos)} artículos con selector alternativo")
                        break
            
            print(f"   Encontrados {len(articulos)} artículos")
            
            for idx, articulo in enumerate(articulos, 1):
                try:
                    # <--- ¡MEJORADO! Extraer título con múltiples estrategias
                    titulo = None
                    
                    # Estrategia 1: Usar selector específico
                    titulo_selector = fuente['selector_titulo']
                    titulo_tag = articulo.find(
                        titulo_selector['name'],
                        titulo_selector.get('attrs', {})
                    )
                    if titulo_tag:
                        titulo = titulo_tag.get_text(strip=True)
                    
                    # Estrategia 2: Si no se encontró, buscar en múltiples lugares comunes
                    if not titulo or titulo == "Sin título":
                        # Buscar en h1, h2, h3 dentro del artículo
                        for tag_name in ['h1', 'h2', 'h3', 'h4']:
                            heading = articulo.find(tag_name)
                            if heading:
                                titulo_candidate = heading.get_text(strip=True)
                                if titulo_candidate and len(titulo_candidate) > 5:  # Evitar títulos muy cortos
                                    titulo = titulo_candidate
                                    break
                    
                    # Estrategia 3: Buscar en el link (atributo title o texto del link)
                    if not titulo or len(titulo) < 5:
                        link_selector = fuente.get('selector_link', {'name': 'a'})
                        link_tag = articulo.find(
                            link_selector['name'],
                            link_selector.get('attrs', {})
                        )
                        if link_tag:
                            # Intentar obtener del atributo title
                            if link_tag.get('title'):
                                titulo = link_tag.get('title').strip()
                            # Si no, obtener del texto del link
                            elif link_tag.get_text(strip=True):
                                link_text = link_tag.get_text(strip=True)
                                if len(link_text) > 5:  # Solo si tiene suficiente texto
                                    titulo = link_text
                    
                    # Estrategia 4: Buscar en elementos con clases comunes de título
                    if not titulo or len(titulo) < 5:
                        for class_pattern in ['title', 'headline', 'titulo', 'noticia-titulo', 'entry-title', 'post-title', 'article-title', 'story-title', 'news-title']:
                            title_elem = articulo.find(attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                            if title_elem:
                                titulo_candidate = title_elem.get_text(strip=True)
                                if titulo_candidate and len(titulo_candidate) > 5:
                                    titulo = titulo_candidate
                                    break
                    
                    # Estrategia 5: Buscar en cualquier elemento con atributo title o aria-label
                    if not titulo or len(titulo) < 5:
                        for elem in articulo.find_all(attrs={'title': True}):
                            title_attr = elem.get('title', '').strip()
                            if title_attr and len(title_attr) > 10:
                                titulo = title_attr
                                break
                    
                    # Estrategia 6: Buscar en el primer elemento con texto significativo
                    if not titulo or len(titulo) < 5:
                        # Buscar en divs, spans, etc. con texto largo
                        for tag in ['div', 'span', 'p']:
                            elems = articulo.find_all(tag, limit=10)
                            for elem in elems:
                                text = elem.get_text(strip=True)
                                # Si tiene más de 20 caracteres y menos de 200, probablemente es un título
                                if 20 < len(text) < 200 and not any(char in text for char in ['http', '@', '.com']):
                                    titulo = text
                                    break
                            if titulo and len(titulo) >= 5:
                                break
                    
                    # Si aún no hay título, usar fallback
                    if not titulo or len(titulo) < 3:
                        titulo = "Sin título"
                    
                    # Extraer link
                    link_selector = fuente.get('selector_link', {'name': 'a'})
                    link_tag = articulo.find(
                        link_selector['name'],
                        link_selector.get('attrs', {})
                    )
                    
                    if link_tag and 'href' in link_tag.attrs:
                        url = link_tag['href']
                        if not url.startswith('http'):
                            url = urljoin(fuente['url'], url)
                    else:
                        # Buscar cualquier link dentro del artículo
                        any_link = articulo.find('a', href=True)
                        if any_link:
                            url = any_link['href']
                            if not url.startswith('http'):
                                url = urljoin(fuente['url'], url)
                        else:
                            url = fuente['url']
                    
                    # <--- ¡MEJORADO! Extraer resumen con múltiples estrategias
                    resumen = None
                    
                    # Estrategia 1: Usar selector específico
                    resumen_selector = fuente['selector_resumen']
                    resumen_tag = articulo.find(
                        resumen_selector['name'],
                        resumen_selector.get('attrs', {})
                    )
                    if resumen_tag:
                        resumen = resumen_tag.get_text(strip=True)
                    
                    # Estrategia 2: Buscar en párrafos comunes
                    if not resumen or resumen == "Sin resumen" or len(resumen) < 10:
                        # Buscar párrafos con clases comunes
                        for class_pattern in ['summary', 'excerpt', 'resumen', 'description', 'descripcion', 'lead']:
                            desc_elem = articulo.find(attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                            if desc_elem:
                                resumen_candidate = desc_elem.get_text(strip=True)
                                if resumen_candidate and len(resumen_candidate) > 10:
                                    resumen = resumen_candidate
                                    break
                    
                    # Estrategia 3: Buscar el primer párrafo con suficiente texto
                    if not resumen or len(resumen) < 10:
                        paragraphs = articulo.find_all('p')
                        for p in paragraphs:
                            p_text = p.get_text(strip=True)
                            # Ignorar párrafos muy cortos (probablemente metadata)
                            if len(p_text) > 20 and len(p_text) < 1000:
                                resumen = p_text
                                break
                    
                    # Estrategia 4: Buscar en divs con clases de descripción
                    if not resumen or len(resumen) < 10:
                        for class_pattern in ['lead', 'intro', 'summary', 'excerpt', 'abstract', 'preview']:
                            desc_elem = articulo.find(attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                            if desc_elem:
                                desc_text = desc_elem.get_text(strip=True)
                                if len(desc_text) > 20:
                                    resumen = desc_text
                                    break
                    
                    # Estrategia 5: Buscar en cualquier elemento con atributo data-description o aria-label
                    if not resumen or len(resumen) < 10:
                        for attr in ['data-description', 'aria-label', 'title']:
                            desc_elem = articulo.find(attrs={attr: True})
                            if desc_elem:
                                desc_text = desc_elem.get(attr, '').strip()
                                if len(desc_text) > 20 and len(desc_text) < 500:
                                    resumen = desc_text
                                    break
                    
                    # Si aún no hay resumen, usar fallback
                    if not resumen or len(resumen) < 5:
                        resumen = "Sin resumen"
                    else:
                        resumen = resumen[:500] if len(resumen) > 500 else resumen
                    
                    # <--- ¡MEJORADO! Extraer imagen con múltiples estrategias
                    imagen_url = None
                    
                    def obtener_url_imagen(img_tag):
                        """Helper para obtener URL de imagen de múltiples atributos"""
                        if not img_tag:
                            return None
                        return (
                            img_tag.get('src') or 
                            img_tag.get('data-src') or 
                            img_tag.get('data-lazy-src') or
                            img_tag.get('data-original') or
                            img_tag.get('data-url') or
                            img_tag.get('data-image') or
                            img_tag.get('data-lazy') or
                            img_tag.get('data-srcset')  # A veces viene en srcset
                        )
                    
                    def es_imagen_valida(img_url, img_tag=None):
                        """Verifica si una imagen es válida (no es icono, no es data URI)"""
                        if not img_url or img_url.startswith('data:'):
                            return False
                        
                        # Filtrar iconos comunes (pero ser menos restrictivo)
                        iconos_comunes = ['favicon', 'sprite']
                        # Solo filtrar si claramente es un icono (no solo contiene la palabra)
                        url_lower = img_url.lower()
                        if any(f'/{icon}.' in url_lower or f'/{icon}/' in url_lower for icon in iconos_comunes):
                            return False
                        
                        # Verificar dimensiones si están disponibles (pero ser más permisivo)
                        if img_tag:
                            width = img_tag.get('width')
                            height = img_tag.get('height')
                            if width and height:
                                try:
                                    w, h = int(width), int(height)
                                    # Filtrar solo imágenes muy pequeñas (menos de 50x50)
                                    if w < 50 or h < 50:
                                        return False
                                except:
                                    pass
                        
                        return True
                    
                    # Estrategia 1: Usar selector específico si existe
                    if fuente.get('selector_imagen'):
                        imagen_selector = fuente['selector_imagen']
                        imagen_tag = articulo.find(
                            imagen_selector['name'],
                            imagen_selector.get('attrs', {})
                        )
                        if imagen_tag:
                            img_url = obtener_url_imagen(imagen_tag)
                            if es_imagen_valida(img_url, imagen_tag):
                                imagen_url = img_url
                    
                    # Estrategia 2: Buscar imágenes con clases comunes
                    if not imagen_url:
                        for class_pattern in ['image', 'img', 'photo', 'picture', 'foto', 'imagen', 'thumbnail', 'thumb']:
                            img_elem = articulo.find('img', attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                            if img_elem:
                                img_url = obtener_url_imagen(img_elem)
                                if es_imagen_valida(img_url, img_elem):
                                    imagen_url = img_url
                                    break
                    
                    # Estrategia 3: Buscar imágenes dentro de links (común en noticias)
                    if not imagen_url:
                        link_with_img = articulo.find('a', href=True)
                        if link_with_img:
                            img_in_link = link_with_img.find('img')
                            if img_in_link:
                                img_url = obtener_url_imagen(img_in_link)
                                if es_imagen_valida(img_url, img_in_link):
                                    imagen_url = img_url
                    
                    # Estrategia 4: Buscar cualquier imagen dentro del artículo (último recurso)
                    if not imagen_url:
                        img_tags = articulo.find_all('img', limit=5)
                        for img in img_tags:
                            img_url = obtener_url_imagen(img)
                            if es_imagen_valida(img_url, img):
                                imagen_url = img_url
                                break
                    
                    # Estrategia 5: Buscar background-image en estilos (menos común)
                    if not imagen_url:
                        style_elem = articulo.find(attrs={'style': lambda x: x and 'background-image' in str(x).lower()})
                        if style_elem:
                            style = style_elem.get('style', '')
                            match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                            if match:
                                bg_url = match.group(1)
                                if es_imagen_valida(bg_url):
                                    imagen_url = bg_url
                    
                    # Convertir URL relativa a absoluta y limpiar
                    if imagen_url:
                        if not imagen_url.startswith('http'):
                            imagen_url = urljoin(fuente['url'], imagen_url)
                        
                        # Limpiar parámetros de tamaño si existen (ej: ?w=300&h=200)
                        if '?' in imagen_url:
                            base_url = imagen_url.split('?')[0]
                            # Mantener solo si parece una URL de imagen válida
                            if any(ext in base_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                                imagen_url = base_url
                            else:
                                # Si no tiene extensión pero tiene parámetros, intentar limpiar parámetros comunes
                                if 'w=' in imagen_url or 'width=' in imagen_url or 'h=' in imagen_url:
                                    # Mantener la URL con parámetros si no tiene extensión clara
                                    pass
                    
                    # <--- ¡MEJORADO! Extraer categoría con múltiples estrategias Y VALIDACIÓN ESTRICTA
                    categoria = None

                    # Estrategia 1: Usar selector específico si existe
                    if fuente.get('selector_categoria'):
                        categoria_selector = fuente['selector_categoria']
                        categoria_tag = articulo.find(
                            categoria_selector['name'],
                            categoria_selector.get('attrs', {})
                        )
                        if categoria_tag:
                            categoria = categoria_tag.get_text(strip=True)

                    # Estrategia 2: Buscar en elementos con clases/atributos comunes de categoría
                    if not categoria or len(categoria) < 2:
                        categorias_comunes = [
                            'category', 'categoria', 'section', 'seccion', 'topic', 'tema', 
                            'tag', 'label', 'etiqueta', 'badge', 'pill', 'kicker'
                        ]
                        
                        for class_pattern in categorias_comunes:
                            # Buscar por clase
                            cat_elem = articulo.find(attrs={'class': lambda x: x and class_pattern in str(x).lower()})
                            if cat_elem:
                                cat_text = cat_elem.get_text(strip=True)
                                # Validar que sea una categoría válida (corta, sin caracteres extraños)
                                if cat_text and 2 < len(cat_text) < 50 and not any(char in cat_text for char in ['http', '@', '.com']):
                                    categoria = cat_text
                                    break
                            
                            # Buscar por data-attribute
                            if not categoria:
                                for attr in ['data-category', 'data-section', 'data-topic', 'data-tag']:
                                    cat_elem = articulo.find(attrs={attr: True})
                                    if cat_elem:
                                        cat_text = cat_elem.get(attr, '').strip()
                                        if cat_text and 2 < len(cat_text) < 50:
                                            categoria = cat_text
                                            break

                    # Estrategia 3: Buscar en links con clases de categoría
                    if not categoria or len(categoria) < 2:
                        cat_link = articulo.find('a', attrs={'class': lambda x: x and any(
                            cat in str(x).lower() for cat in ['category', 'section', 'topic', 'tag']
                        )})
                        if cat_link:
                            cat_text = cat_link.get_text(strip=True)
                            if cat_text and 2 < len(cat_text) < 50:
                                categoria = cat_text

                    # Estrategia 4: Buscar en elementos span con texto corto (común en badges)
                    if not categoria or len(categoria) < 2:
                        spans = articulo.find_all('span', limit=10)
                        for span in spans:
                            span_text = span.get_text(strip=True)
                            # Si es corto, en mayúsculas/capitalizado, y está al inicio, probablemente es categoría
                            if span_text and 3 <= len(span_text) <= 30:
                                # Verificar que no sea fecha, hora, o número
                                if not re.match(r'^\d+', span_text) and not any(word in span_text.lower() for word in ['ago', 'min', 'hour', 'day', 'hace', 'hora']):
                                    # Si tiene todas las palabras capitalizadas, probablemente es categoría
                                    palabras = span_text.split()
                                    if palabras and all(p[0].isupper() if p else False for p in palabras):
                                        categoria = span_text
                                        break

                    # Estrategia 5: Inferir desde la URL (último recurso)
                    if not categoria or len(categoria) < 2:
                        if url and url != fuente['url']:
                            # Parsear la URL para extraer sección
                            parsed_url = urlparse(url)
                            path_parts = [p for p in parsed_url.path.split('/') if p]
                            
                            # Buscar secciones comunes en la URL
                            secciones_conocidas = [
                                'deportes', 'sports', 'tecnologia', 'technology', 'tech',
                                'politica', 'politics', 'economia', 'economy', 'business',
                                'salud', 'health', 'ciencia', 'science', 'cultura', 'culture',
                                'entretenimiento', 'entertainment', 'mundo', 'world', 'internacional',
                                'nacional', 'local', 'educacion', 'education', 'finanzas', 'finance'
                            ]
                            
                            for part in path_parts[:3]:  # Solo revisar las primeras 3 partes
                                part_lower = part.lower()
                                if part_lower in secciones_conocidas:
                                    # Capitalizar primera letra
                                    categoria = part.capitalize()
                                    break

                    # ✅ VALIDACIÓN Y NORMALIZACIÓN ESTRICTA DE CATEGORÍA
                    if categoria:
                        # Eliminar caracteres especiales al inicio/final
                        categoria = categoria.strip('|•·- »«›‹')
                        
                        # ✅ FILTRAR HORAS (10:16 h, 10:19 h, etc.)
                        if re.search(r'\d+:\d+\s*h', categoria, re.IGNORECASE):
                            categoria = None
                        
                        # ✅ FILTRAR SI ES SOLO NÚMEROS O NÚMEROS CON DOS PUNTOS
                        elif re.match(r'^[\d\s:]+$', categoria):
                            categoria = None
                        
                        # ✅ FILTRAR SI CONTIENE P.M. O A.M.
                        elif re.search(r'(p\.m\.|a\.m\.)', categoria, re.IGNORECASE):
                            categoria = None
                        
                        # ✅ FILTRAR PALABRAS PROHIBIDAS COMUNES
                        elif categoria:
                            palabras_prohibidas = [
                                'getty', 'live', 'actualidad', 'último', 'últimas', 'hoy',
                                'ayer', 'ahora', 'breaking', 'destacado', 'principal',
                                'ver más', 'leer más', 'continuar', 'siguiente', 'desde las',
                                'lo último', 'premios', 'playoff', 'basketball', 'football'
                            ]
                            if any(palabra in categoria.lower() for palabra in palabras_prohibidas):
                                categoria = None
                        
                        # ✅ FILTRAR LUGARES GEOGRÁFICOS COMUNES
                        if categoria:
                            lugares_prohibidos = [
                                'lima', 'méxico', 'perú', 'argentina', 'colombia', 'chile',
                                'estados unidos', 'eeuu', 'usa', 'la libertad', 'arequipa',
                                'cusco', 'piura', 'trujillo'
                            ]
                            if categoria.lower() in lugares_prohibidos:
                                categoria = None
                        
                        # ✅ FILTRAR SI TIENE SÍMBOLOS EXTRAÑOS
                        if categoria and any(char in categoria for char in ['»', '«', '›', '‹', '...', '::']):
                            categoria = None
                        
                        # Capitalizar correctamente
                        if categoria and categoria.isupper():
                            categoria = categoria.title()
                        
                        # Limitar longitud
                        if categoria and (len(categoria) < 3 or len(categoria) > 30):
                            categoria = None
                        
                        # ✅ NORMALIZAR CATEGORÍAS SIMILARES
                        if categoria:
                            categoria_lower = categoria.lower()
                            
                            # Mapeo de categorías similares
                            mapeo_categorias = {
                                'tecnologia': 'Tecnología',
                                'politica': 'Política',
                                'economia': 'Economía',
                                'espectaculos': 'Espectáculos',
                                'internacional': 'Internacionales',
                                'policiales': 'Sociedad',
                                'gobierno': 'Política',
                                'ncaa': 'Deportes',
                                'college': 'Deportes',
                                'soccer': 'Deportes',
                                'fútbol': 'Deportes',
                                'futbol': 'Deportes'
                            }
                            
                            # Buscar si hay mapeo exacto
                            if categoria_lower in mapeo_categorias:
                                categoria = mapeo_categorias[categoria_lower]
                            # Buscar si contiene alguna palabra clave
                            else:
                                for key, value in mapeo_categorias.items():
                                    if key in categoria_lower:
                                        categoria = value
                                        break
                    
                    # <--- ¡MEJORADO! Siempre intentar scraping profundo si faltan datos críticos
                    fecha_publicacion = None
                    
                    # Determinar si necesitamos scraping profundo
                    necesita_scraping_profundo = (
                        (not titulo or titulo == "Sin título" or len(titulo) < 5) or
                        (not imagen_url) or
                        (not resumen or resumen == "Sin resumen" or len(resumen) < 20)
                    )
                    
                    # Hacer scraping profundo SIEMPRE que tengamos una URL válida y falten datos
                    if necesita_scraping_profundo and url and url != fuente['url'] and url.startswith('http'):
                        print(f"      🔍 Datos incompletos, haciendo scraping profundo de: {url[:60]}...")
                        try:
                            datos_profundos = self._scrapear_pagina_individual(url, titulo if titulo and titulo != "Sin título" else None)
                            
                            # Usar datos del scraping profundo si son mejores
                            if datos_profundos.get('titulo') and (not titulo or titulo == "Sin título" or len(titulo) < 5):
                                titulo = datos_profundos['titulo']
                                print(f"         ✓ Título obtenido del scraping profundo")
                            
                            if datos_profundos.get('imagen_url') and not imagen_url:
                                imagen_url = datos_profundos['imagen_url']
                                print(f"         ✓ Imagen obtenida del scraping profundo")
                            
                            if datos_profundos.get('resumen') and (not resumen or resumen == "Sin resumen" or len(resumen) < 20):
                                resumen = datos_profundos['resumen']
                                print(f"         ✓ Resumen obtenido del scraping profundo: {resumen[:50]}...")
                            
                            if datos_profundos.get('fecha_publicacion'):
                                fecha_publicacion = datos_profundos['fecha_publicacion']
                                print(f"         ✓ Fecha obtenida del scraping profundo")
                            
                            # Pequeña pausa para no sobrecargar el servidor
                            time.sleep(0.3)
                        except Exception as e:
                            print(f"         ⚠️ Error en scraping profundo: {e}")
                    
                    # Si aún no hay título válido, usar fallback
                    if not titulo or titulo == "Sin título" or len(titulo) < 3:
                        titulo = "Sin título"
                    
                    # Si aún no hay resumen válido, usar fallback
                    if not resumen or resumen == "Sin resumen" or len(resumen) < 5:
                        resumen = "Sin resumen"
                    else:
                        resumen = resumen[:500] if len(resumen) > 500 else resumen
                    
                    noticia = {
                        'titulo': titulo,
                        'url': url,
                        'resumen': resumen,
                        'imagen_url': imagen_url,
                        'categoria': categoria,
                        'fecha_publicacion': fecha_publicacion,
                        'fuente': fuente['nombre'],
                        'fuente_id': fuente['id']
                    }
                    
                    if guardar:
                        # user_id debe ser pasado desde el endpoint
                        # Por ahora, si no hay user_id, no guardamos (o lanzamos error)
                        if not hasattr(self, '_current_user_id'):
                            print(f"   ⚠️ No hay user_id configurado, saltando guardado")
                        else:
                            noticia_id = self.db.guardar_noticia(noticia, self._current_user_id)
                            if noticia_id:
                                noticia['id'] = noticia_id
                    
                    noticias.append(noticia)
                    imagen_info = f" [Imagen: {'✓' if imagen_url else '✗'}]"
                    categoria_info = f" [Categoría: {categoria or 'N/A'}]"
                    fecha_info = f" [Fecha: {'✓' if fecha_publicacion else '✗'}]"
                    print(f"   ✓ Artículo {idx}: {titulo[:50]}...{imagen_info}{categoria_info}{fecha_info}")
                    
                except Exception as e:
                    print(f"   ✗ Error procesando artículo {idx}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"✅ {fuente['nombre']}: {len(noticias)} noticias obtenidas\n")
            
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout en {fuente['nombre']}\n")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión en {fuente['nombre']}: {e}\n")
        except Exception as e:
            print(f"❌ Error inesperado en {fuente['nombre']}: {e}\n")
        
        return noticias
    
    def scrape_todas_fuentes(self, limite: int = 5, guardar: bool = True, solo_activas: bool = True, user_id: Optional[int] = None) -> List[Dict]:
        """Scrapea todas las fuentes activas"""
        # Guardar user_id temporalmente para usar en guardar_noticia
        self._current_user_id = user_id
        print("\n" + "="*60)
        print("🚀 INICIANDO SCRAPING DE NOTICIAS")
        print("="*60 + "\n")
        
        todas = []
        # Obtener solo las fuentes del usuario (o todas si es admin)
        # Para obtener fuentes del usuario, necesitamos pasar user_id y es_admin
        # Por ahora, si user_id es None, no scrapeamos nada
        if user_id is None:
            print("⚠️ No se puede scrapear sin user_id")
            return []
        
        # Asumimos que no es admin por defecto (el endpoint debería pasar esto)
        fuentes = self.obtener_fuentes(solo_activas=solo_activas, user_id=user_id, es_admin=False)
        
        if not fuentes:
            print(f"⚠️ No hay fuentes disponibles para el usuario {user_id}")
            return []
        
        print(f"📋 Total de fuentes a scrapear: {len(fuentes)}\n")
        
        for idx, fuente in enumerate(fuentes, 1):
            print(f"[{idx}/{len(fuentes)}] ", end="")
            noticias = self.scrape_fuente(fuente, limite, guardar, user_id)
            todas.extend(noticias)
            
            if idx < len(fuentes):
                time.sleep(2)
        
        print("="*60)
        print(f"✅ SCRAPING COMPLETADO: {len(todas)} noticias totales")
        print("="*60 + "\n")
        
        return todas
    
    # ==================== GESTIÓN DE NOTICIAS ====================
    
    def obtener_noticias_guardadas(
        self, 
        limite: int = 50, 
        offset: int = 0,
        fuente_id: Optional[int] = None,
        categoria: Optional[str] = None,
        user_id: Optional[int] = None,
        es_admin: bool = False
    ):
        """Obtiene noticias guardadas en la BD. Retorna (noticias, total)"""
        return self.db.obtener_noticias(limite, offset, fuente_id, categoria, user_id, es_admin)
    
    def contar_noticias(self, user_id: Optional[int] = None, es_admin: bool = False) -> int:
        """Cuenta el total de noticias guardadas (filtrado por usuario si no es admin)"""
        return self.db.contar_noticias(user_id, es_admin)
    
    def limpiar_noticias(self, user_id: Optional[int] = None, es_admin: bool = False) -> bool:
        """Elimina noticias de la BD (del usuario o todas si es admin)"""
        return self.db.limpiar_noticias(user_id, es_admin)
    
    def obtener_categorias(self, user_id: Optional[int] = None, es_admin: bool = False) -> List[str]:
        """Obtiene todas las categorías únicas (filtrado por usuario si no es admin)"""
        return self.db.obtener_categorias(user_id, es_admin)