import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
import json
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self):
        """Configuración de conexión a PostgreSQL"""
        self.config = {
            'host': 'localhost',
            'user': 'postgres',
            'password': '',  # ⚠️ CAMBIA ESTO
            'database': 'noticias_db',
            'port': 5432
        }
    
    def get_connection(self):
        """Crea y retorna una conexión a la base de datos"""
        try:
            connection = psycopg2.connect(**self.config)
            return connection
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            return None
    
    def crear_tablas(self):
        """Crea las tablas necesarias si no existen"""
        connection = self.get_connection()
        if not connection:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = connection.cursor()
        
        try:
            # <--- ¡NUEVA TABLA! Usuarios para autenticación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre_usuario VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    contrasena_hash VARCHAR(255) NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Tabla de fuentes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fuentes (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    url VARCHAR(512) NOT NULL,
                    selector_contenedor JSONB NOT NULL,
                    selector_titulo JSONB NOT NULL,
                    selector_resumen JSONB NOT NULL,
                    selector_link JSONB,
                    selector_imagen JSONB,
                    selector_categoria JSONB,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de noticias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS noticias (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(512) NOT NULL,
                    url VARCHAR(1024) NOT NULL UNIQUE,
                    resumen TEXT,
                    imagen_url VARCHAR(1024),
                    categoria VARCHAR(255),
                    fuente_id INTEGER REFERENCES fuentes(id) ON DELETE CASCADE,
                    fecha_publicacion TIMESTAMP,
                    fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Agregar columna fecha_publicacion si no existe (para bases de datos existentes)
            try:
                cursor.execute("""
                    ALTER TABLE noticias 
                    ADD COLUMN IF NOT EXISTS fecha_publicacion TIMESTAMP
                """)
            except:
                pass  # La columna ya existe o no se puede agregar
            
            # Crear índices para mejor rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_noticias_fuente 
                ON noticias(fuente_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_noticias_fecha 
                ON noticias(fecha_scraping DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_noticias_url 
                ON noticias(url)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_noticias_categoria 
                ON noticias(categoria)
            """)
            
            # Índices para usuarios
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_usuarios_nombre_usuario 
                ON usuarios(nombre_usuario)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_usuarios_email 
                ON usuarios(email)
            """)
            
            connection.commit()
            print("✅ Tablas creadas exitosamente (incluyendo usuarios)")
            return True
            
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()
    
    # ==================== OPERACIONES DE USUARIOS ====================
    
    def crear_usuario(self, nombre_usuario: str, email: str, contrasena: str) -> Optional[Dict]:
        """Crea un nuevo usuario con contraseña hasheada"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Hashear la contraseña
        contrasena_hash = generate_password_hash(contrasena)
        
        query = """
            INSERT INTO usuarios (nombre_usuario, email, contrasena_hash)
            VALUES (%s, %s, %s)
            RETURNING id, nombre_usuario, email, fecha_creacion, activo
        """
        
        try:
            cursor.execute(query, (nombre_usuario, email, contrasena_hash))
            usuario = dict(cursor.fetchone())
            connection.commit()
            print(f"✅ Usuario '{nombre_usuario}' creado exitosamente")
            return usuario
        except psycopg2.IntegrityError as e:
            connection.rollback()
            if 'nombre_usuario' in str(e):
                print(f"❌ Error: El nombre de usuario '{nombre_usuario}' ya existe")
                return {'error': 'nombre_usuario_existe'}
            elif 'email' in str(e):
                print(f"❌ Error: El email '{email}' ya existe")
                return {'error': 'email_existe'}
            return {'error': 'constraint_violation'}
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()
    
    def obtener_usuario_por_nombre(self, nombre_usuario: str) -> Optional[Dict]:
        """Obtiene un usuario por nombre de usuario (incluye contraseña hash)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT id, nombre_usuario, email, contrasena_hash, fecha_creacion, activo
                FROM usuarios 
                WHERE nombre_usuario = %s
            """, (nombre_usuario,))
            
            usuario = cursor.fetchone()
            return dict(usuario) if usuario else None
            
        except Exception as e:
            print(f"❌ Error obteniendo usuario: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def obtener_usuario_por_email(self, email: str) -> Optional[Dict]:
        """Obtiene un usuario por email"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT id, nombre_usuario, email, contrasena_hash, fecha_creacion, activo
                FROM usuarios 
                WHERE email = %s
            """, (email,))
            
            usuario = cursor.fetchone()
            return dict(usuario) if usuario else None
            
        except Exception as e:
            print(f"❌ Error obteniendo usuario: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def verificar_contrasena(self, contrasena: str, contrasena_hash: str) -> bool:
        """Verifica si una contraseña coincide con su hash"""
        return check_password_hash(contrasena_hash, contrasena)
    
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict]:
        """Obtiene un usuario por ID (sin incluir contraseña)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT id, nombre_usuario, email, fecha_creacion, activo
                FROM usuarios 
                WHERE id = %s
            """, (usuario_id,))
            
            usuario = cursor.fetchone()
            return dict(usuario) if usuario else None
            
        except Exception as e:
            print(f"❌ Error obteniendo usuario: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    # ==================== OPERACIONES DE FUENTES ====================
    
    def agregar_fuente(self, fuente: Dict) -> Optional[Dict]:
        """Agrega una nueva fuente a la BD"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        query = """
            INSERT INTO fuentes (nombre, url, selector_contenedor, selector_titulo, 
                               selector_resumen, selector_link, selector_imagen, selector_categoria, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        
        values = (
            fuente['nombre'],
            fuente['url'],
            json.dumps(fuente['selector_contenedor']),
            json.dumps(fuente['selector_titulo']),
            json.dumps(fuente['selector_resumen']),
            json.dumps(fuente.get('selector_link', {'name': 'a'})),
            json.dumps(fuente.get('selector_imagen', {'name': 'img'})),
            json.dumps(fuente.get('selector_categoria')),
            fuente.get('activo', True)
        )
        
        try:
            cursor.execute(query, values)
            nueva_fuente = dict(cursor.fetchone())
            connection.commit()
            print(f"✅ Fuente '{fuente['nombre']}' agregada")
            return nueva_fuente
        except Exception as e:
            print(f"❌ Error agregando fuente: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()
    
    def obtener_fuentes(self, solo_activas: bool = False) -> List[Dict]:
        """Obtiene todas las fuentes"""
        connection = self.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        if solo_activas:
            query = "SELECT * FROM fuentes WHERE activo = TRUE ORDER BY id"
        else:
            query = "SELECT * FROM fuentes ORDER BY id"
        
        try:
            cursor.execute(query)
            fuentes = [dict(row) for row in cursor.fetchall()]
            return fuentes
        except Exception as e:
            print(f"❌ Error obteniendo fuentes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    def obtener_fuente(self, fuente_id: int) -> Optional[Dict]:
        """Obtiene una fuente por ID"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("SELECT * FROM fuentes WHERE id = %s", (fuente_id,))
            fuente = cursor.fetchone()
            return dict(fuente) if fuente else None
        except Exception as e:
            print(f"❌ Error obteniendo fuente: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def actualizar_fuente(self, fuente_id: int, datos: Dict) -> Optional[Dict]:
        """Actualiza una fuente existente"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        
        campos = []
        valores = []
        
        if 'nombre' in datos:
            campos.append("nombre = %s")
            valores.append(datos['nombre'])
        if 'url' in datos:
            campos.append("url = %s")
            valores.append(datos['url'])
        if 'selector_contenedor' in datos:
            campos.append("selector_contenedor = %s")
            valores.append(json.dumps(datos['selector_contenedor']))
        if 'selector_titulo' in datos:
            campos.append("selector_titulo = %s")
            valores.append(json.dumps(datos['selector_titulo']))
        if 'selector_resumen' in datos:
            campos.append("selector_resumen = %s")
            valores.append(json.dumps(datos['selector_resumen']))
        if 'selector_link' in datos:
            campos.append("selector_link = %s")
            valores.append(json.dumps(datos['selector_link']))
        if 'selector_imagen' in datos:
            campos.append("selector_imagen = %s")
            valores.append(json.dumps(datos['selector_imagen']))
        if 'selector_categoria' in datos:
            campos.append("selector_categoria = %s")
            valores.append(json.dumps(datos['selector_categoria']))
        if 'activo' in datos:
            campos.append("activo = %s")
            valores.append(datos['activo'])
        
        if not campos:
            return None
        
        campos.append("fecha_actualizacion = CURRENT_TIMESTAMP")
        valores.append(fuente_id)
        
        query = f"UPDATE fuentes SET {', '.join(campos)} WHERE id = %s"
        
        try:
            cursor.execute(query, valores)
            connection.commit()
            print(f"✅ Fuente ID {fuente_id} actualizada")
            return self.obtener_fuente(fuente_id)
        except Exception as e:
            print(f"❌ Error actualizando fuente: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()
    
    def eliminar_fuente(self, fuente_id: int) -> bool:
        """Elimina una fuente"""
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("DELETE FROM fuentes WHERE id = %s", (fuente_id,))
            connection.commit()
            success = cursor.rowcount > 0
            if success:
                print(f"✅ Fuente ID {fuente_id} eliminada")
            return success
        except Exception as e:
            print(f"❌ Error eliminando fuente: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()
    
    # ==================== OPERACIONES DE NOTICIAS ====================
    
    def guardar_noticia(self, noticia: Dict) -> Optional[int]:
        """Guarda una noticia en la BD (evita duplicados por URL)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        query = """
            INSERT INTO noticias (titulo, url, resumen, imagen_url, categoria, fuente_id, fecha_publicacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO UPDATE SET 
                titulo = EXCLUDED.titulo,
                resumen = EXCLUDED.resumen,
                imagen_url = EXCLUDED.imagen_url,
                categoria = EXCLUDED.categoria,
                fecha_publicacion = EXCLUDED.fecha_publicacion,
                fecha_scraping = CURRENT_TIMESTAMP
            RETURNING id
        """
        
        values = (
            noticia['titulo'],
            noticia['url'],
            noticia.get('resumen', ''),
            noticia.get('imagen_url'),
            noticia.get('categoria'),
            noticia.get('fuente_id'),
            noticia.get('fecha_publicacion')
        )
        
        try:
            cursor.execute(query, values)
            noticia_id = cursor.fetchone()[0]
            connection.commit()
            return noticia_id
        except Exception as e:
            print(f"❌ Error guardando noticia: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()
    
    def obtener_noticias(
        self, 
        limite: int = 50, 
        offset: int = 0,
        fuente_id: Optional[int] = None,
        categoria: Optional[str] = None
    ):
        """Obtiene noticias de la BD con paginación y filtros. Retorna (noticias, total)"""
        connection = self.get_connection()
        if not connection:
            return [], 0
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Construir query base para contar y obtener
        where_clause = "WHERE 1=1"
        parametros = []
        
        if fuente_id is not None:
            where_clause += " AND n.fuente_id = %s"
            parametros.append(int(fuente_id))  # Asegurar que sea int
        
        if categoria:
            where_clause += " AND n.categoria = %s"
            parametros.append(categoria)
        
        # Primero contar el total
        count_query = f"""
            SELECT COUNT(*) as total
            FROM noticias n
            LEFT JOIN fuentes f ON n.fuente_id = f.id
            {where_clause}
        """
        
        try:
            # Ejecutar count query
            cursor.execute(count_query, parametros)
            total = cursor.fetchone()['total']
            
            # Luego obtener las noticias
            query = f"""
                SELECT n.*, f.nombre as fuente_nombre
                FROM noticias n
                LEFT JOIN fuentes f ON n.fuente_id = f.id
                {where_clause}
                ORDER BY n.fecha_scraping DESC LIMIT %s OFFSET %s
            """
            query_params = parametros.copy()  # Copiar parámetros para no modificar la lista original
            query_params.extend([limite, offset])
            
            cursor.execute(query, query_params)
            
            noticias = []
            for row in cursor.fetchall():
                noticia = dict(row)
                noticia['fuente'] = noticia.pop('fuente_nombre', 'Desconocida')
                noticia['fecha_scraping'] = str(noticia['fecha_scraping'])
                if noticia.get('fecha_publicacion'):
                    noticia['fecha_publicacion'] = str(noticia['fecha_publicacion'])
                noticias.append(noticia)
            
            return noticias, total
        except Exception as e:
            print(f"❌ Error obteniendo noticias: {e}")
            return [], 0
        finally:
            cursor.close()
            connection.close()
    
    def contar_noticias(self) -> int:
        """Cuenta el total de noticias en la BD"""
        connection = self.get_connection()
        if not connection:
            return 0
        
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM noticias")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"❌ Error contando noticias: {e}")
            return 0
        finally:
            cursor.close()
            connection.close()
    
    def limpiar_noticias(self) -> bool:
        """Elimina todas las noticias (útil para pruebas)"""
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM noticias")
            connection.commit()
            print("✅ Todas las noticias eliminadas")
            return True
        except Exception as e:
            print(f"❌ Error limpiando noticias: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()
    
    def obtener_categorias(self) -> List[str]:
        """Obtiene todas las categorías únicas de noticias"""
        connection = self.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                SELECT DISTINCT categoria 
                FROM noticias 
                WHERE categoria IS NOT NULL 
                ORDER BY categoria
            """)
            
            categorias = [row[0] for row in cursor.fetchall()]
            return categorias
            
        except Exception as e:
            print(f"❌ Error obteniendo categorías: {e}")
            return []
        finally:
            cursor.close()
            connection.close()