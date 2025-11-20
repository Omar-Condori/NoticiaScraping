from database import Database
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class Estadisticas:
    def __init__(self):
        self.db = Database()
    
    def obtener_estadisticas_generales(self, user_id: Optional[int] = None, es_admin: bool = False) -> Dict:
        """
        Obtiene estadísticas generales del sistema
        Si user_id es None o es_admin es True, muestra stats globales
        Si user_id está presente y no es admin, filtra por usuario
        """
        connection = self.db.get_connection()
        if not connection:
            return {}
        
        cursor = connection.cursor()
        
        try:
            # Determinar si filtrar por usuario
            filtro_usuario = "" if es_admin or user_id is None else f"WHERE n.user_id = {user_id}"
            filtro_fuentes = "" if es_admin or user_id is None else f"WHERE user_id = {user_id}"
            
            # Total de noticias
            cursor.execute(f"SELECT COUNT(*) FROM noticias n {filtro_usuario}")
            total_noticias = cursor.fetchone()[0]
            
            # Total de fuentes (del usuario o todas si es admin)
            cursor.execute(f"SELECT COUNT(*) FROM fuentes {filtro_fuentes}")
            total_fuentes = cursor.fetchone()[0]
            
            # Fuentes activas
            cursor.execute(f"""
                SELECT COUNT(*) FROM fuentes 
                WHERE activo = TRUE {('AND user_id = %s' if not es_admin and user_id else '')}
            """, (user_id,) if not es_admin and user_id else ())
            fuentes_activas = cursor.fetchone()[0]
            
            # Noticias por fuente
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT f.nombre, COUNT(n.id) as total
                    FROM fuentes f
                    LEFT JOIN noticias n ON f.id = n.fuente_id
                    GROUP BY f.id, f.nombre
                    ORDER BY total DESC
                """)
            else:
                cursor.execute("""
                    SELECT f.nombre, COUNT(n.id) as total
                    FROM fuentes f
                    LEFT JOIN noticias n ON f.id = n.fuente_id AND n.user_id = %s
                    WHERE f.user_id = %s
                    GROUP BY f.id, f.nombre
                    ORDER BY total DESC
                """, (user_id, user_id))
            
            noticias_por_fuente = [
                {'fuente': row[0], 'total': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Noticias de las últimas 24 horas
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '24 hours'
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '24 hours'
                    AND user_id = %s
                """, (user_id,))
            noticias_24h = cursor.fetchone()[0]
            
            # Noticias de la última semana
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '7 days'
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '7 days'
                    AND user_id = %s
                """, (user_id,))
            noticias_semana = cursor.fetchone()[0]
            
            # Última noticia scrapeada
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT titulo, fecha_scraping 
                    FROM noticias 
                    ORDER BY fecha_scraping DESC 
                    LIMIT 1
                """)
            else:
                cursor.execute("""
                    SELECT titulo, fecha_scraping 
                    FROM noticias 
                    WHERE user_id = %s
                    ORDER BY fecha_scraping DESC 
                    LIMIT 1
                """, (user_id,))
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
            import traceback
            traceback.print_exc()
            return {}
        finally:
            cursor.close()
            connection.close()
    
    def obtener_tendencias(self, dias: int = 7, user_id: Optional[int] = None, es_admin: bool = False) -> List[Dict]:
        """Obtiene tendencias de scraping por día (filtradas por usuario si no es admin)"""
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT 
                        DATE(fecha_scraping) as fecha,
                        COUNT(*) as total_noticias
                    FROM noticias
                    WHERE fecha_scraping >= NOW() - INTERVAL '%s days'
                    GROUP BY DATE(fecha_scraping)
                    ORDER BY fecha DESC
                """, (dias,))
            else:
                cursor.execute("""
                    SELECT 
                        DATE(fecha_scraping) as fecha,
                        COUNT(*) as total_noticias
                    FROM noticias
                    WHERE fecha_scraping >= NOW() - INTERVAL '%s days'
                    AND user_id = %s
                    GROUP BY DATE(fecha_scraping)
                    ORDER BY fecha DESC
                """, (dias, user_id))
            
            tendencias = [
                {'fecha': str(row[0]), 'total': row[1]}
                for row in cursor.fetchall()
            ]
            
            return tendencias
            
        except Exception as e:
            print(f"❌ Error obteniendo tendencias: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            connection.close()
    
    def obtener_top_fuentes(self, limite: int = 5, user_id: Optional[int] = None, es_admin: bool = False) -> List[Dict]:
        """Obtiene las fuentes con más noticias (filtradas por usuario si no es admin)"""
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            if es_admin or user_id is None:
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
            else:
                cursor.execute("""
                    SELECT 
                        f.nombre,
                        f.url,
                        COUNT(n.id) as total_noticias,
                        MAX(n.fecha_scraping) as ultima_actualizacion
                    FROM fuentes f
                    LEFT JOIN noticias n ON f.id = n.fuente_id AND n.user_id = %s
                    WHERE f.user_id = %s
                    GROUP BY f.id, f.nombre, f.url
                    ORDER BY total_noticias DESC
                    LIMIT %s
                """, (user_id, user_id, limite))
            
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
            import traceback
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            connection.close()
