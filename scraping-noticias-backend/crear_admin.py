"""
Script para crear el primer usuario administrador
Ejecutar: python crear_admin.py
"""
from database import Database
from werkzeug.security import generate_password_hash

def crear_admin():
    db = Database()
    
    # Datos del admin (cambiar según necesidad)
    nombre_usuario = 'admin'
    email = 'admin@noticias.com'
    contrasena = 'admin123'  # ⚠️ CAMBIAR EN PRODUCCIÓN
    
    connection = db.get_connection()
    if not connection:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor()
    
    try:
        # Verificar si ya existe un admin
        cursor.execute("SELECT id FROM usuarios WHERE rol = 'admin' LIMIT 1")
        if cursor.fetchone():
            print("⚠️ Ya existe un usuario administrador")
            respuesta = input("¿Deseas crear otro admin? (s/n): ")
            if respuesta.lower() != 's':
                return
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
        if cursor.fetchone():
            print(f"⚠️ El usuario '{nombre_usuario}' ya existe")
            respuesta = input("¿Deseas actualizarlo a admin? (s/n): ")
            if respuesta.lower() == 's':
                cursor.execute(
                    "UPDATE usuarios SET rol = 'admin', contrasena_hash = %s WHERE nombre_usuario = %s",
                    (generate_password_hash(contrasena), nombre_usuario)
                )
                connection.commit()
                print(f"✅ Usuario '{nombre_usuario}' actualizado a administrador")
                return
        
        # Crear nuevo admin
        contrasena_hash = generate_password_hash(contrasena)
        cursor.execute("""
            INSERT INTO usuarios (nombre_usuario, email, contrasena_hash, rol)
            VALUES (%s, %s, %s, 'admin')
            RETURNING id, nombre_usuario, email, rol
        """, (nombre_usuario, email, contrasena_hash))
        
        admin = cursor.fetchone()
        connection.commit()
        
        print("="*60)
        print("✅ USUARIO ADMINISTRADOR CREADO EXITOSAMENTE")
        print("="*60)
        print(f"Nombre de usuario: {admin[1]}")
        print(f"Email: {admin[2]}")
        print(f"Rol: {admin[3]}")
        print(f"Contraseña: {contrasena}")
        print("="*60)
        print("⚠️ IMPORTANTE: Cambia la contraseña después del primer login")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error creando admin: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    crear_admin()

