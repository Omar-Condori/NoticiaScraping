"""
Módulo INDEPENDIENTE para scraping histórico usando sitemaps XML
VERSIÓN CORREGIDA - Manejo correcto de timezones
"""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import time

class ScrapingHistorico:
    def __init__(self, db, scraper=None):
        self.db = db
        self.scraper = scraper
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def url_ya_existe(self, url: str) -> bool:
        """Verifica si una URL ya está en la base de datos"""
        connection = self.db.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM noticias WHERE url = %s LIMIT 1", (url,))
            return cursor.fetchone() is not None
        except:
            return False
        finally:
            cursor.close()
            connection.close()
    
    def obtener_sitemap_urls(
        self, 
        sitemap_url: str, 
        fecha_desde: datetime = None,
        fecha_hasta: datetime = None
    ) -> List[Dict]:
        """
        Extrae URLs de un sitemap XML filtradas por fecha
        ✅ VERSIÓN CORREGIDA: Manejo correcto de timezones
        """
        try:
            response = requests.get(sitemap_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            urls = []
            
            # Verificar si es un índice de sitemaps
            for sitemap in root.findall('ns:sitemap', ns):
                loc = sitemap.find('ns:loc', ns)
                if loc is not None:
                    sub_urls = self.obtener_sitemap_urls(loc.text, fecha_desde, fecha_hasta)
                    urls.extend(sub_urls)
            
            # Buscar URLs individuales
            for url_elem in root.findall('ns:url', ns):
                loc = url_elem.find('ns:loc', ns)
                lastmod = url_elem.find('ns:lastmod', ns)
                
                if loc is not None:
                    url_data = {'url': loc.text, 'lastmod': None}
                    
                    if lastmod is not None:
                        try:
                            # Parsear fecha y asegurar que tenga timezone
                            fecha_str = lastmod.text.replace('Z', '+00:00')
                            fecha_dt = datetime.fromisoformat(fecha_str)
                            
                            # ✅ Si no tiene timezone, agregar UTC
                            if fecha_dt.tzinfo is None:
                                fecha_dt = fecha_dt.replace(tzinfo=timezone.utc)
                            
                            url_data['lastmod'] = fecha_dt
                        except:
                            pass
                    
                    # ✅ FILTRO CON MANEJO CORRECTO DE TIMEZONES
                    if url_data['lastmod']:
                        # Verificar fecha_desde
                        if fecha_desde and url_data['lastmod'] < fecha_desde:
                            continue
                        
                        # Verificar fecha_hasta
                        if fecha_hasta and url_data['lastmod'] > fecha_hasta:
                            continue
                        
                        urls.append(url_data)
                    elif not fecha_desde and not fecha_hasta:
                        urls.append(url_data)
            
            return urls
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def detectar_sitemap(self, url_base: str) -> Optional[str]:
        """Detecta la URL del sitemap de un sitio"""
        posibles = [
            urljoin(url_base, '/sitemap.xml'),
            urljoin(url_base, '/sitemap_index.xml'),
            urljoin(url_base, '/news-sitemap.xml'),
        ]
        
        for sitemap_url in posibles:
            try:
                response = requests.head(sitemap_url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    return sitemap_url
            except:
                continue
        
        # Buscar en robots.txt
        try:
            robots_url = urljoin(url_base, '/robots.txt')
            response = requests.get(robots_url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        return line.split(':', 1)[1].strip()
        except:
            pass
        
        return None
    
    def scraping_historico_fuente(
        self,
        fuente: Dict,
        dias_desde: int = 15,
        dias_hasta: int = 3,
        limite_urls: int = 500,
        user_id: int = None
    ) -> Dict:
        """
        Scrapea noticias HISTÓRICAS de una fuente usando su sitemap
        ✅ VERSIÓN CORREGIDA
        """
        print(f"\n{'='*70}")
        print(f"🕒 SCRAPING HISTÓRICO: {fuente['nombre']}")
        print(f"{'='*70}")
        
        # ✅ Calcular fechas CON TIMEZONE UTC
        ahora = datetime.now(timezone.utc)
        fecha_desde = ahora - timedelta(days=dias_desde)
        fecha_hasta = ahora - timedelta(days=dias_hasta)
        
        print(f"📅 Rango de fechas:")
        print(f"   Desde: {fecha_desde.strftime('%Y-%m-%d')} (hace {dias_desde} días)")
        print(f"   Hasta: {fecha_hasta.strftime('%Y-%m-%d')} (hace {dias_hasta} días)")
        print(f"   ✅ Esto evita duplicar noticias recientes")
        
        # Detectar sitemap
        sitemap_url = self.detectar_sitemap(fuente['url'])
        if not sitemap_url:
            print(f"   ⚠️ No se encontró sitemap")
            return {'success': False, 'error': 'Sin sitemap'}
        
        print(f"   ✅ Sitemap: {sitemap_url}")
        print(f"   🔍 Extrayendo URLs del sitemap...")
        
        # Obtener URLs
        urls = self.obtener_sitemap_urls(sitemap_url, fecha_desde, fecha_hasta)
        
        if not urls:
            print(f"   ⚠️ No se encontraron URLs en el rango de fechas")
            return {'success': False, 'error': 'Sin URLs en rango'}
        
        print(f"   📊 URLs encontradas: {len(urls)}")
        
        # Limitar
        if len(urls) > limite_urls:
            urls = urls[:limite_urls]
            print(f"   ⚠️ Limitando a {limite_urls} URLs")
        
        # Estadísticas
        stats = {
            'total_urls': len(urls),
            'ya_existian': 0,
            'scrapeadas': 0,
            'guardadas': 0,
            'errores': 0
        }
        
        print(f"\n   🚀 Iniciando scraping...")
        
        # Procesar URLs
        for idx, url_data in enumerate(urls, 1):
            try:
                url = url_data['url']
                
                # Verificar duplicado
                if self.url_ya_existe(url):
                    stats['ya_existian'] += 1
                    if idx % 50 == 0:
                        print(f"   [{idx}/{len(urls)}] {stats['guardadas']} nuevas | {stats['ya_existian']} duplicadas")
                    continue
                
                # Scrapear
                if self.scraper:
                    datos = self.scraper._scrapear_pagina_individual(url)
                else:
                    datos = {
                        'titulo': url.split('/')[-1].replace('-', ' ').title(),
                        'resumen': 'Noticia histórica',
                        'imagen_url': None,
                        'fecha_publicacion': url_data.get('lastmod')
                    }
                
                if datos and datos.get('titulo'):
                    stats['scrapeadas'] += 1
                    
                    noticia = {
                        'titulo': datos['titulo'],
                        'url': url,
                        'resumen': datos.get('resumen', 'Sin resumen'),
                        'imagen_url': datos.get('imagen_url'),
                        'categoria': None,
                        'fecha_publicacion': datos.get('fecha_publicacion') or url_data.get('lastmod'),
                        'fuente': fuente['nombre'],
                        'fuente_id': fuente['id']
                    }
                    
                    try:
                        noticia_id = self.db.guardar_noticia(noticia, user_id)
                        if noticia_id:
                            stats['guardadas'] += 1
                    except Exception as e:
                        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                            stats['ya_existian'] += 1
                        else:
                            stats['errores'] += 1
                
                if idx % 50 == 0:
                    print(f"   [{idx}/{len(urls)}] ✅ {stats['guardadas']} nuevas | ⏭️  {stats['ya_existian']} duplicadas | ❌ {stats['errores']} errores")
                
                time.sleep(0.3)
                
            except KeyboardInterrupt:
                print(f"\n   ⚠️ Interrumpido por el usuario")
                break
            except Exception as e:
                stats['errores'] += 1
                continue
        
        # Resumen
        print(f"\n   {'='*66}")
        print(f"   ✅ COMPLETADO: {fuente['nombre']}")
        print(f"   📊 Estadísticas:")
        print(f"      • URLs procesadas: {stats['total_urls']}")
        print(f"      • Noticias nuevas guardadas: {stats['guardadas']}")
        print(f"      • Ya existían: {stats['ya_existian']}")
        print(f"      • Errores: {stats['errores']}")
        print(f"   {'='*66}\n")
        
        stats['success'] = True
        return stats
