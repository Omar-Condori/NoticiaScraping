"""
Script para verificar y corregir la estructura de la base de datos
Ejecutar: python verificar_db.py
"""
from database import Database

def verificar_y_corregir():
    db = Database()
    connection = db.get_connection()
    
    if not connection:
        print("❌ No se pudo conectar a la base de datos")
        print("⚠️ Verifica:")
        print("   1. Que PostgreSQL esté corriendo")
        print("   2. Que la base de datos 'noticias_db' exista")
        print("   3. Que las credenciales en database.py sean correctas")
        return False
    
    cursor = connection.cursor()
    
    try:
        # Verificar si la tabla usuarios existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'usuarios'
            );
        """)
        tabla_existe = cursor.fetchone()[0]
        
        if not tabla_existe:
            print("❌ La tabla 'usuarios' no existe")
            print("✅ Ejecutando crear_tablas()...")
            db.crear_tablas()
            print("✅ Tablas creadas")
        else:
            print("✅ La tabla 'usuarios' existe")
            
            # Verificar si la columna rol existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'usuarios' AND column_name = 'rol'
                );
            """)
            columna_existe = cursor.fetchone()[0]
            
            if not columna_existe:
                print("⚠️ La columna 'rol' no existe, agregándola...")
                cursor.execute("""
                    ALTER TABLE usuarios 
                    ADD COLUMN rol VARCHAR(20) DEFAULT 'usuario'
                """)
                cursor.execute("""
                    UPDATE usuarios 
                    SET rol = 'usuario' 
                    WHERE rol IS NULL
                """)
                try:
                    cursor.execute("""
                        ALTER TABLE usuarios 
                        ADD CONSTRAINT check_rol 
                        CHECK (rol IN ('admin', 'usuario'))
                    """)
                except:
                    pass  # La constraint ya existe
                connection.commit()
                print("✅ Columna 'rol' agregada")
            else:
                print("✅ La columna 'rol' existe")
                
                # Verificar usuarios sin rol
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol IS NULL")
                sin_rol = cursor.fetchone()[0]
                if sin_rol > 0:
                    print(f"⚠️ Hay {sin_rol} usuarios sin rol, actualizando...")
                    cursor.execute("UPDATE usuarios SET rol = 'usuario' WHERE rol IS NULL")
                    connection.commit()
                    print("✅ Usuarios actualizados")
        
        # Verificar estructura de la tabla
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'usuarios'
            ORDER BY ordinal_position
        """)
        columnas = cursor.fetchall()
        print("\n📋 Estructura de la tabla 'usuarios':")
        for col in columnas:
            print(f"   - {col[0]}: {col[1]} (default: {col[2]})")
        
        connection.commit()
        print("\n✅ Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    verificar_y_corregir()

