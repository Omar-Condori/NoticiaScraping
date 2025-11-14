from database import Database
from typing import Dict, List
from datetime import datetime, timedelta

class Estadisticas:
    def __init__(self):
        self.db = Database()
    
    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales del sistema"""
        connection = self.db.get_connection()
        if not connection:
            return {}
        
        cursor = connection.cursor()
        
        try:
            # Total de noticias
            cursor.execute("SELECT COUNT(*) FROM noticias")
            total_noticias = cursor.fetchone()[0]
            
            # Total de fuentes
            cursor.execute("SELECT COUNT(*) FROM fuentes")
            total_fuentes = cursor.fetchone()[0]
            
            # Fuentes activas
            cursor.execute("SELECT COUNT(*) FROM fuentes WHERE activo = TRUE")
            fuentes_activas = cursor.fetchone()[0]
            
            # Noticias por fuente
            cursor.execute("""
                SELECT f.nombre, COUNT(n.id) as total
                FROM fuentes f
                LEFT JOIN noticias n ON f.id = n.fuente_id
                GROUP BY f.id, f.nombre
                ORDER BY total DESC
            """)
            noticias_por_fuente = [
                {'fuente': row[0], 'total': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Noticias de las últimas 24 horas
            cursor.execute("""
                SELECT COUNT(*) FROM noticias 
                WHERE fecha_scraping >= NOW() - INTERVAL '24 hours'
            """)
            noticias_24h = cursor.fetchone()[0]
            
            # Noticias de la última semana
            cursor.execute("""
                SELECT COUNT(*) FROM noticias 
                WHERE fecha_scraping >= NOW() - INTERVAL '7 days'
            """)
            noticias_semana = cursor.fetchone()[0]
            
            # Última noticia scrapeada
            cursor.execute("""
                SELECT titulo, fecha_scraping 
                FROM noticias 
                ORDER BY fecha_scraping DESC 
                LIMIT 1
            """)
            ultima_noticia = cursor.fetchone()
            
            return {
                'resumen': {
                    'total_noticias': total_noticias,
                    'total_fuentes': total_fuentes,
                    'fuentes_activas': fuentes_activas,
                    'noticias_24h': noticias_24h,
                    'noticias_semana': noticias_semana
                },
                'por_fuente': noticias_por_fuente,
                'ultima_actualizacion': {
                    'titulo': ultima_noticia[0] if ultima_noticia else None,
                    'fecha': str(ultima_noticia[1]) if ultima_noticia else None
                }
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}
        finally:
            cursor.close()
            connection.close()
    
    def obtener_tendencias(self, dias: int = 7) -> List[Dict]:
        """Obtiene tendencias de scraping por día"""
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    DATE(fecha_scraping) as fecha,
                    COUNT(*) as total_noticias
                FROM noticias
                WHERE fecha_scraping >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(fecha_scraping)
                ORDER BY fecha DESC
            """, (dias,))
            
            tendencias = [
                {'fecha': str(row[0]), 'total': row[1]}
                for row in cursor.fetchall()
            ]
            
            return tendencias
            
        except Exception as e:
            print(f"❌ Error obteniendo tendencias: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def obtener_top_fuentes(self, limite: int = 5) -> List[Dict]:
        """Obtiene las fuentes con más noticias"""
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    f.nombre,
                    f.url,
                    COUNT(n.id) as total_noticias,
                    MAX(n.fecha_scraping) as ultima_actualizacion
                FROM fuentes f
                LEFT JOIN noticias n ON f.id = n.fuente_id
                GROUP BY f.id, f.nombre, f.url
                ORDER BY total_noticias DESC
                LIMIT %s
            """, (limite,))
            
            top_fuentes = [
                {
                    'nombre': row[0],
                    'url': row[1],
                    'total_noticias': row[2],
                    'ultima_actualizacion': str(row[3]) if row[3] else None
                }
                for row in cursor.fetchall()
            ]
            
            return top_fuentes
            
        except Exception as e:
            print(f"❌ Error obteniendo top fuentes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()