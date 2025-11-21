#!/usr/bin/env python3
"""
Script para actualizar el campo 'pais' en noticias existentes
basándose en la URL de su fuente.
"""

import sys
sys.path.append('/Users/omarcondori/Documents/PROYECTOS/NOTICIA/scraping-noticias-backend')

from database import Database
from scraper import NewsScraper

def actualizar_paises_noticias():
    """Actualiza el campo pais de todas las noticias existentes"""
    print("🔄 Iniciando actualización de países en noticias...")
    
    db = Database()
    scraper = NewsScraper()
    
    # Obtener todas las fuentes
    connection = db.get_connection()
    if not connection:
        print("❌ Error conectando a la base de datos")
        return
    
    cursor = connection.cursor()
    
    try:
        # Obtener todas las fuentes
        cursor.execute("SELECT id, url FROM fuentes")
        fuentes = cursor.fetchall()
        
        print(f"📋 Encontradas {len(fuentes)} fuentes")
        
        actualizadas = 0
        for fuente_id, url in fuentes:
            # Detectar país de la fuente
            pais = scraper._detectar_pais(url)
            
            if pais:
                # Actualizar todas las noticias de esta fuente
                cursor.execute("""
                    UPDATE noticias 
                    SET pais = %s 
                    WHERE fuente_id = %s AND (pais IS NULL OR pais = '')
                """, (pais, fuente_id))
                
                count = cursor.rowcount
                if count > 0:
                    print(f"  ✅ Fuente ID {fuente_id} ({url}): {count} noticias → {pais}")
                    actualizadas += count
            else:
                print(f"  ⚠️ No se pudo detectar país para: {url}")
        


        connection.commit()
        print(f"\n✅ Actualización completada: {actualizadas} noticias actualizadas")
        
        # Mostrar estadísticas
        cursor.execute("SELECT pais, COUNT(*) FROM noticias WHERE pais IS NOT NULL GROUP BY pais ORDER BY COUNT(*) DESC")
        stats = cursor.fetchall()
        
        if stats:
            print("\n📊 Distribución de noticias por país:")
            for pais, count in stats:
                print(f"  {pais}: {count} noticias")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    actualizar_paises_noticias()
