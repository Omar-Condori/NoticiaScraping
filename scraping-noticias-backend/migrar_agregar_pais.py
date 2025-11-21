#!/usr/bin/env python3
"""
Script robusto para agregar la columna pais a la tabla noticias
"""

import psycopg2

def migrar_agregar_pais():
    """Agrega la columna pais a la tabla noticias si no existe"""
    print("🔄 Iniciando migración: agregar columna 'pais'...")
    
    # Configuración de conexión
    config = {
        'host': 'localhost',
        'user': 'postgres',
        'password': '',  # Cambiar si tienes contraseña
        'database': 'noticias_db',
        'port': 5432
    }
    
    try:
        # Conectar a la base de datos
        connection = psycopg2.connect(**config)
        connection.autocommit = True  # Auto-commit para evitar problemas de transacción
        cursor = connection.cursor()
        
        print("✅ Conectado a la base de datos")
        
        # Verificar si la columna existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'noticias' AND column_name = 'pais'
        """)
        
        existe = cursor.fetchone()
        
        if existe:
            print("ℹ️  La columna 'pais' ya existe")
        else:
            # Agregar la columna
            print("📝 Agregando columna 'pais' a tabla noticias...")
            cursor.execute("""
                ALTER TABLE noticias 
                ADD COLUMN pais VARCHAR(100)
            """)
            print("✅ Columna 'pais' agregada exitosamente")
        
        # Crear índice si no existe
        print("📝 Creando índice para columna 'pais'...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_noticias_pais ON noticias(pais)
        """)
        print("✅ Índice creado exitosamente")
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM noticias")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM noticias WHERE pais IS NOT NULL")
        con_pais = cursor.fetchone()[0]
        
        print(f"\n📊 Estadísticas:")
        print(f"  Total de noticias: {total}")
        print(f"  Noticias con país: {con_pais}")
        print(f"  Noticias sin país: {total - con_pais}")
        
        if total - con_pais > 0:
            print(f"\n💡 Ejecuta 'python3 actualizar_paises.py' para asignar países a las noticias existentes")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    migrar_agregar_pais()
