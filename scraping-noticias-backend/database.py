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
                    rol VARCHAR(20) DEFAULT 'usuario' CHECK (rol IN ('admin', 'usuario')),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Agregar columna rol si no existe (para bases de datos existentes)
            try:
                cursor.execute("""
                    ALTER TABLE usuarios 
                    ADD COLUMN IF NOT EXISTS rol VARCHAR(20) DEFAULT 'usuario'
                """)
                # Actualizar usuarios existentes sin rol
                cursor.execute("""
                    UPDATE usuarios 
                    SET rol = 'usuario' 
                    WHERE rol IS NULL
                """)
                # Intentar agregar constraint (puede fallar si ya existe)
                try:
                    cursor.execute("""
                        ALTER TABLE usuarios 
                        ADD CONSTRAINT check_rol 
                        CHECK (rol IN ('admin', 'usuario'))
                    """)
                except:
                    pass  # La constraint ya existe
            except Exception as e:
                print(f"⚠️ Advertencia al agregar columna rol: {e}")
                pass
            
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
                    user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Agregar columna user_id si no existe (para bases de datos existentes)
            try:
                cursor.execute("""
                    ALTER TABLE fuentes 
                    ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE
                """)
                # Actualizar fuentes existentes sin user_id (asignar a un usuario admin si existe, o NULL)
                cursor.execute("""
                    UPDATE fuentes 
                    SET user_id = (SELECT id FROM usuarios WHERE rol = 'admin' LIMIT 1)
                    WHERE user_id IS NULL AND EXISTS (SELECT 1 FROM usuarios WHERE rol = 'admin')
                """)
            except Exception as e:
                print(f"⚠️ Advertencia al agregar columna user_id a fuentes: {e}")
                pass
            
            # Crear índice para mejor rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fuentes_user_id 
                ON fuentes(user_id)
            """)
            
            # Tabla de noticias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS noticias (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(512) NOT NULL,
                    url VARCHAR(1024) NOT NULL,
                    resumen TEXT,
                    imagen_url VARCHAR(1024),
                    categoria VARCHAR(255),
                    fuente_id INTEGER REFERENCES fuentes(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    fecha_publicacion TIMESTAMP,
                    fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(url, user_id)
                )
            """)
            
            # Agregar columna user_id si no existe (para bases de datos existentes)
            try:
                cursor.execute("""
                    ALTER TABLE noticias 
                    ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE
                """)
                # Eliminar constraint UNIQUE de url si existe y crear nuevo con user_id
                try:
                    cursor.execute("""
                        ALTER TABLE noticias 
                        DROP CONSTRAINT IF EXISTS noticias_url_key
                    """)
                except:
                    pass
                # Crear índice único compuesto
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_noticias_url_user 
                    ON noticias(url, user_id)
                """)
            except:
                pass
            
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
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_noticias_user_id 
                ON noticias(user_id)
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
            INSERT INTO usuarios (nombre_usuario, email, contrasena_hash, rol)
            VALUES (%s, %s, %s, 'usuario')
            RETURNING id, nombre_usuario, email, rol, fecha_creacion, activo
        """
        
        try:
            cursor.execute(query, (nombre_usuario, email, contrasena_hash))
            usuario_row = cursor.fetchone()
            if not usuario_row:
                print(f"❌ Error: No se pudo crear el usuario (fetchone retornó None)")
                connection.rollback()
                return None
            usuario = dict(usuario_row)
            # Asegurar que el rol esté presente
            if 'rol' not in usuario:
                usuario['rol'] = 'usuario'
            connection.commit()
            print(f"✅ Usuario '{nombre_usuario}' creado exitosamente con rol: {usuario.get('rol', 'usuario')}")
            return usuario
        except psycopg2.IntegrityError as e:
            connection.rollback()
            error_str = str(e)
            print(f"❌ IntegrityError al crear usuario: {error_str}")
            if 'nombre_usuario' in error_str or 'usuarios_nombre_usuario_key' in error_str:
                print(f"❌ Error: El nombre de usuario '{nombre_usuario}' ya existe")
                return {'error': 'nombre_usuario_existe'}
            elif 'email' in error_str or 'usuarios_email_key' in error_str:
                print(f"❌ Error: El email '{email}' ya existe")
                return {'error': 'email_existe'}
            print(f"❌ Error de integridad desconocido: {error_str}")
            return {'error': 'constraint_violation', 'detalle': error_str}
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            import traceback
            traceback.print_exc()
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
                SELECT id, nombre_usuario, email, contrasena_hash, rol, fecha_creacion, activo
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
                SELECT id, nombre_usuario, email, contrasena_hash, rol, fecha_creacion, activo
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
                SELECT id, nombre_usuario, email, rol, fecha_creacion, activo
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
    
    def agregar_fuente(self, fuente: Dict, user_id: int) -> Optional[Dict]:
        """Agrega una nueva fuente a la BD (asociada a un usuario)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        query = """
            INSERT INTO fuentes (nombre, url, selector_contenedor, selector_titulo, 
                               selector_resumen, selector_link, selector_imagen, selector_categoria, user_id, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            user_id,
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
    
    def obtener_fuentes(self, solo_activas: bool = False, user_id: Optional[int] = None, es_admin: bool = False) -> List[Dict]:
        """Obtiene fuentes (filtradas por usuario si no es admin)"""
        connection = self.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Construir query con filtros
        where_clauses = []
        params = []
        
        # Filtrar por usuario (admin ve todas)
        if not es_admin and user_id is not None:
            where_clauses.append("user_id = %s")
            params.append(int(user_id))
        
        # Filtrar por activas
        if solo_activas:
            where_clauses.append("activo = TRUE")
        
        # Construir query final
        where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        query = f"SELECT * FROM fuentes{where_clause} ORDER BY id"
        
        try:
            cursor.execute(query, params)
            fuentes = [dict(row) for row in cursor.fetchall()]
            return fuentes
        except Exception as e:
            print(f"❌ Error obteniendo fuentes: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            connection.close()
    
    def obtener_fuente(self, fuente_id: int, user_id: Optional[int] = None, es_admin: bool = False) -> Optional[Dict]:
        """Obtiene una fuente por ID (verifica que pertenezca al usuario si no es admin)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Si es admin, puede ver cualquier fuente
            if es_admin:
                cursor.execute("SELECT * FROM fuentes WHERE id = %s", (fuente_id,))
            elif user_id is not None:
                # Usuario normal solo puede ver sus propias fuentes
                cursor.execute("SELECT * FROM fuentes WHERE id = %s AND user_id = %s", (fuente_id, int(user_id)))
            else:
                # Sin user_id, no puede ver nada
                return None
            
            fuente = cursor.fetchone()
            return dict(fuente) if fuente else None
        except Exception as e:
            print(f"❌ Error obteniendo fuente: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            connection.close()
    
    def actualizar_fuente(self, fuente_id: int, datos: Dict, user_id: Optional[int] = None, es_admin: bool = False) -> Optional[Dict]:
        """Actualiza una fuente existente (verifica que pertenezca al usuario si no es admin)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        
        # Verificar que la fuente pertenezca al usuario (si no es admin)
        if not es_admin and user_id is not None:
            cursor.execute("SELECT user_id FROM fuentes WHERE id = %s", (fuente_id,))
            resultado = cursor.fetchone()
            if not resultado or resultado[0] != user_id:
                print(f"❌ Usuario {user_id} no tiene permiso para actualizar fuente {fuente_id}")
                return None
        
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
            return self.obtener_fuente(fuente_id, user_id, es_admin)
        except Exception as e:
            print(f"❌ Error actualizando fuente: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()
    
    def eliminar_fuente(self, fuente_id: int, user_id: Optional[int] = None, es_admin: bool = False) -> bool:
        """Elimina una fuente (verifica que pertenezca al usuario si no es admin)"""
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            # Verificar que la fuente pertenezca al usuario (si no es admin)
            if not es_admin and user_id is not None:
                cursor.execute("SELECT user_id FROM fuentes WHERE id = %s", (fuente_id,))
                resultado = cursor.fetchone()
                if not resultado or resultado[0] != user_id:
                    print(f"❌ Usuario {user_id} no tiene permiso para eliminar fuente {fuente_id}")
                    return False
            
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
    
    def guardar_noticia(self, noticia: Dict, user_id: int) -> Optional[int]:
        """Guarda una noticia en la BD (evita duplicados por URL+user_id)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        query = """
            INSERT INTO noticias (titulo, url, resumen, imagen_url, categoria, fuente_id, user_id, fecha_publicacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url, user_id) DO UPDATE SET 
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
            user_id,
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
        categoria: Optional[str] = None,
        user_id: Optional[int] = None,
        es_admin: bool = False
    ):
        """Obtiene noticias de la BD con paginación y filtros. Retorna (noticias, total)"""
        connection = self.get_connection()
        if not connection:
            return [], 0
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Construir query base para contar y obtener
        where_clause = "WHERE 1=1"
        parametros = []
        
        # Filtrar por usuario (admin ve todas)
        if not es_admin and user_id is not None:
            where_clause += " AND n.user_id = %s"
            parametros.append(int(user_id))
        
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
    
    def contar_noticias(self, user_id: Optional[int] = None, es_admin: bool = False) -> int:
        """Cuenta el total de noticias en la BD (filtrado por usuario si no es admin)"""
        connection = self.get_connection()
        if not connection:
            return 0
        
        cursor = connection.cursor()
        try:
            query = "SELECT COUNT(*) FROM noticias"
            params = []
            
            # Filtrar por usuario si no es admin
            if not es_admin and user_id is not None:
                query += " WHERE user_id = %s"
                params.append(int(user_id))
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"❌ Error contando noticias: {e}")
            return 0
        finally:
            cursor.close()
            connection.close()
    
    def limpiar_noticias(self, user_id: Optional[int] = None, es_admin: bool = False) -> bool:
        """Elimina noticias (del usuario o todas si es admin)"""
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            if es_admin:
                cursor.execute("DELETE FROM noticias")
                print("✅ Todas las noticias eliminadas (admin)")
            elif user_id is not None:
                cursor.execute("DELETE FROM noticias WHERE user_id = %s", (int(user_id),))
                print(f"✅ Noticias del usuario {user_id} eliminadas")
            else:
                print("⚠️ No se puede limpiar: falta user_id o permisos de admin")
                return False
            
            connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error limpiando noticias: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()
    
    def obtener_categorias(self, user_id: Optional[int] = None, es_admin: bool = False) -> List[str]:
        """Obtiene todas las categorías únicas de noticias (filtrado por usuario si no es admin)"""
        connection = self.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            query = """
                SELECT DISTINCT categoria 
                FROM noticias 
                WHERE categoria IS NOT NULL
            """
            params = []
            
            # Filtrar por usuario si no es admin
            if not es_admin and user_id is not None:
                query += " AND user_id = %s"
                params.append(int(user_id))
            
            query += " ORDER BY categoria"
            
            cursor.execute(query, params)
            categorias = [row[0] for row in cursor.fetchall()]
            return categorias
            
        except Exception as e:
            print(f"❌ Error obteniendo categorías: {e}")
            return []
        finally:
            cursor.close()
            connection.close()