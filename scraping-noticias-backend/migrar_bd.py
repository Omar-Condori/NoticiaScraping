#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar la columna pais
"""

import sys
sys.path.append('/Users/omarcondori/Documents/PROYECTOS/NOTICIA/scraping-noticias-backend')

from database import Database

def migrar_bd():
    """Ejecuta las migraciones de la base de datos"""
    print("🔄 Iniciando migración de base de datos...")
    
    db = Database()
    
    # Ejecutar crear_tablas que debería agregar la columna pais
    resultado = db.crear_tablas()
    
    if resultado:
        print("✅ Migración completada exitosamente")
        print("✅ La columna 'pais' ha sido agregada a la tabla noticias")
    else:
        print("❌ Error en la migración")
    
    return resultado

if __name__ == '__main__':
    migrar_bd()
