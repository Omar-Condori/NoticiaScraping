from database import Database
from typing import List, Dict, Optional
from datetime import datetime

class BusquedaAvanzada:
    def __init__(self):
        self.db = Database()
    
    def buscar_noticias(
        self,
        query: Optional[str] = None,
        fuente_id: Optional[int] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        limite: int = 50,
        orden: str = 'DESC'
    ) -> List[Dict]:
        """
        Búsqueda avanzada de noticias
        
        Args:
            query: Término de búsqueda (busca en título y resumen)
            fuente_id: ID de fuente específica
            fecha_desde: Fecha desde (formato: YYYY-MM-DD)
            fecha_hasta: Fecha hasta (formato: YYYY-MM-DD)
            limite: Número máximo de resultados
            orden: Orden de resultados (ASC o DESC)
        """
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        # Construir query SQL dinámicamente
        sql_query = """
            SELECT 
                n.id,
                n.titulo,
                n.url,
                n.resumen,
                n.fecha_scraping,
                f.nombre as fuente_nombre,
                f.id as fuente_id
            FROM noticias n
            LEFT JOIN fuentes f ON n.fuente_id = f.id
            WHERE 1=1
        """
        
        parametros = []
        
        # Filtro por búsqueda de texto
        if query:
            sql_query += """
                AND (
                    LOWER(n.titulo) LIKE LOWER(%s) 
                    OR LOWER(n.resumen) LIKE LOWER(%s)
                )
            """
            search_pattern = f"%{query}%"
            parametros.extend([search_pattern, search_pattern])
        
        # Filtro por fuente
        if fuente_id:
            sql_query += " AND n.fuente_id = %s"
            parametros.append(fuente_id)
        
        # Filtro por fecha desde
        if fecha_desde:
            sql_query += " AND DATE(n.fecha_scraping) >= %s"
            parametros.append(fecha_desde)
        
        # Filtro por fecha hasta
        if fecha_hasta:
            sql_query += " AND DATE(n.fecha_scraping) <= %s"
            parametros.append(fecha_hasta)
        
        # Orden y límite
        orden_sql = 'ASC' if orden.upper() == 'ASC' else 'DESC'
        sql_query += f" ORDER BY n.fecha_scraping {orden_sql} LIMIT %s"
        parametros.append(limite)
        
        try:
            cursor.execute(sql_query, parametros)
            
            noticias = []
            for row in cursor.fetchall():
                noticias.append({
                    'id': row[0],
                    'titulo': row[1],
                    'url': row[2],
                    'resumen': row[3],
                    'fecha_scraping': str(row[4]),
                    'fuente': row[5],
                    'fuente_id': row[6]
                })
            
            return noticias
            
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def buscar_por_palabras_clave(self, palabras: List[str], limite: int = 50) -> List[Dict]:
        """Busca noticias que contengan cualquiera de las palabras clave"""
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        # Construir condiciones OR para cada palabra
        condiciones = []
        parametros = []
        
        for palabra in palabras:
            condiciones.append("(LOWER(n.titulo) LIKE LOWER(%s) OR LOWER(n.resumen) LIKE LOWER(%s))")
            search_pattern = f"%{palabra}%"
            parametros.extend([search_pattern, search_pattern])
        
        sql_query = f"""
            SELECT 
                n.id,
                n.titulo,
                n.url,
                n.resumen,
                n.fecha_scraping,
                f.nombre as fuente_nombre
            FROM noticias n
            LEFT JOIN fuentes f ON n.fuente_id = f.id
            WHERE {' OR '.join(condiciones)}
            ORDER BY n.fecha_scraping DESC
            LIMIT %s
        """
        parametros.append(limite)
        
        try:
            cursor.execute(sql_query, parametros)
            
            noticias = []
            for row in cursor.fetchall():
                noticias.append({
                    'id': row[0],
                    'titulo': row[1],
                    'url': row[2],
                    'resumen': row[3],
                    'fecha_scraping': str(row[4]),
                    'fuente': row[5]
                })
            
            return noticias
            
        except Exception as e:
            print(f"❌ Error en búsqueda por palabras clave: {e}")
            return []
        finally:
            cursor.close()
            connection.close()