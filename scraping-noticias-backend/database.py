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
    
    # ==================== OPERACIONES DE ESQUEMA ====================
    
    def crear_tablas(self):
        """Crea las tablas necesarias si no existen (usuarios, fuentes, noticias, planes, suscripciones, pagos, scraping_diario)"""
        connection = self.get_connection()
        if not connection:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = connection.cursor()
        
        try:
            # --- TABLA: usuarios
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
            
            # Agregado de columna rol si no existe (para bases de datos existentes)
            try:
                cursor.execute("""
                    ALTER TABLE usuarios 
                    ADD COLUMN IF NOT EXISTS rol VARCHAR(20) DEFAULT 'usuario'
                """)
                cursor.execute("UPDATE usuarios SET rol = 'usuario' WHERE rol IS NULL")
                try:
                    cursor.execute("""
                        ALTER TABLE usuarios 
                        ADD CONSTRAINT check_rol 
                        CHECK (rol IN ('admin', 'usuario'))
                    """)
                except:
                    pass
            except Exception as e:
                print(f"⚠️ Advertencia al agregar columna rol a usuarios: {e}")
                pass
            
            # --- TABLA: planes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS planes (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    precio NUMERIC(10, 2) NOT NULL,
                    limite_fuentes INTEGER NOT NULL DEFAULT 5,
                    limite_scraping_diario INTEGER NOT NULL DEFAULT 30,
                    descripcion TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Agregar columna limite_scraping_diario si no existe
            try:
                cursor.execute("""
                    ALTER TABLE planes 
                    ADD COLUMN IF NOT EXISTS limite_scraping_diario INTEGER NOT NULL DEFAULT 30
                """)
            except Exception as e:
                print(f"⚠️ Advertencia al agregar columna limite_scraping_diario: {e}")
                pass
            
            # --- TABLA: suscripciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suscripciones (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    plan_id INTEGER REFERENCES planes(id) ON DELETE RESTRICT,
                    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_vencimiento TIMESTAMP NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    cancelado BOOLEAN DEFAULT FALSE,
                    UNIQUE(user_id, activo)
                )
            """)
            
            # --- TABLA: pagos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    plan_id INTEGER REFERENCES planes(id) ON DELETE RESTRICT,
                    metodo_pago VARCHAR(50) NOT NULL,
                    monto NUMERIC(10, 2) NOT NULL,
                    referencia_pago VARCHAR(255) UNIQUE,
                    datos_pago JSONB,
                    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'completado', 'fallido', 'reembolsado')),
                    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_verificacion TIMESTAMP,
                    verificado_por INTEGER REFERENCES usuarios(id) ON DELETE SET NULL
                )
            """)
            
            # --- TABLA: fuentes
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
            
            # Agregado de columna user_id si no existe a fuentes
            try:
                cursor.execute("""
                    ALTER TABLE fuentes 
                    ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE
                """)
                cursor.execute("""
                    UPDATE fuentes 
                    SET user_id = (SELECT id FROM usuarios WHERE rol = 'admin' LIMIT 1)
                    WHERE user_id IS NULL AND EXISTS (SELECT 1 FROM usuarios WHERE rol = 'admin')
                """)
            except Exception as e:
                print(f"⚠️ Advertencia al agregar columna user_id a fuentes: {e}")
                pass
            
            # --- TABLA: noticias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS noticias (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(512) NOT NULL,
                    url VARCHAR(1024) NOT NULL,
                    resumen TEXT,
                    imagen_url VARCHAR(1024),
                    categoria VARCHAR(255),
                    pais VARCHAR(100),
                    fuente_id INTEGER REFERENCES fuentes(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    fecha_publicacion TIMESTAMP,
                    fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(url, user_id)
                )
            """)
            
            # Agregado de columna user_id y UNIQUE constraint si no existe a noticias
            try:
                cursor.execute("""
                    ALTER TABLE noticias 
                    ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE
                """)
                try:
                    cursor.execute("""
                        ALTER TABLE noticias 
                        DROP CONSTRAINT IF EXISTS noticias_url_key
                    """)
                except:
                    pass
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_noticias_url_user 
                    ON noticias(url, user_id)
                """)
            except:
                pass
            
            # Agregado de columna fecha_publicacion si no existe a noticias
            try:
                cursor.execute("""
                    ALTER TABLE noticias 
                    ADD COLUMN IF NOT EXISTS fecha_publicacion TIMESTAMP
                """)
            except:
                pass
            
            # Agregado de columna pais si no existe a noticias
            try:
                cursor.execute("""
                    ALTER TABLE noticias 
                    ADD COLUMN IF NOT EXISTS pais VARCHAR(100)
                """)
            except:
                pass
            
            # --- TABLA: scraping_diario (✅ NUEVO)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraping_diario (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
                    cantidad INTEGER NOT NULL DEFAULT 0,
                    plan_id INTEGER REFERENCES planes(id) ON DELETE SET NULL,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, fecha)
                )
            """)
            
            # --- Índices ---
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fuentes_user_id ON fuentes(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_fuente ON noticias(fuente_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_fecha ON noticias(fecha_scraping DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_url ON noticias(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON noticias(categoria)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_pais ON noticias(pais)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_user_id ON noticias(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_nombre_usuario ON usuarios(nombre_usuario)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_suscripciones_user_active ON suscripciones(user_id, activo)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraping_diario_user_fecha ON scraping_diario(user_id, fecha)")
            
            connection.commit()
            print("✅ Tablas creadas exitosamente (incluyendo usuarios, planes, suscripciones, pagos y scraping_diario)")
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

    # ==================== OPERACIONES DE PLANES ====================

    def obtener_planes(self) -> List[Dict]:
        """Obtiene todos los planes disponibles"""
        connection = self.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT id, nombre, precio, limite_fuentes, limite_scraping_diario, descripcion, activo
                FROM planes 
                WHERE activo = TRUE
                ORDER BY precio ASC
            """)
            planes = [dict(row) for row in cursor.fetchall()]
            return planes
        except Exception as e:
            print(f"❌ Error obteniendo planes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def obtener_plan(self, plan_id: int) -> Optional[Dict]:
        """Obtiene un plan por ID"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("SELECT * FROM planes WHERE id = %s", (plan_id,))
            plan = cursor.fetchone()
            return dict(plan) if plan else None
        except Exception as e:
            print(f"❌ Error obteniendo plan: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    # ==================== OPERACIONES DE SUSCRIPCIONES ====================

    def obtener_suscripcion_activa(self, user_id: int) -> Optional[Dict]:
        """Obtiene la suscripción activa de un usuario"""
        connection = self.get_connection()
        if not connection:
            return None
    
        cursor = connection.cursor(cursor_factory=RealDictCursor)
    
        try:
            cursor.execute("""
                SELECT s.*, p.nombre as plan_nombre, p.precio, p.limite_fuentes, p.limite_scraping_diario, p.descripcion
                FROM suscripciones s
                JOIN planes p ON s.plan_id = p.id
                WHERE s.user_id = %s AND s.activo = TRUE AND s.cancelado = FALSE
                ORDER BY s.fecha_inicio DESC
                LIMIT 1
            """, (user_id,))
            
            suscripcion = cursor.fetchone()
            return dict(suscripcion) if suscripcion else None
        except Exception as e:
            print(f"❌ Error obteniendo suscripción: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    def crear_suscripcion(self, user_id: int, plan_id: int, meses: int = 1) -> Optional[Dict]:
        """Crea o actualiza la suscripción de un usuario"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Desactivar suscripción anterior si existe
            cursor.execute("""
                UPDATE suscripciones 
                SET activo = FALSE, cancelado = TRUE
                WHERE user_id = %s AND activo = TRUE
            """, (user_id,))
            
            # Crear nueva suscripción
            cursor.execute("""
                INSERT INTO suscripciones (user_id, plan_id, fecha_vencimiento, activo)
                VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '%s months', TRUE)
                RETURNING *
            """, (user_id, plan_id, meses))
            
            nueva_suscripcion = dict(cursor.fetchone())
            connection.commit()
            print(f"✅ Suscripción creada para usuario {user_id} al plan {plan_id}")
            return nueva_suscripcion
        except Exception as e:
            print(f"❌ Error creando suscripción: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()

    def verificar_limite_fuentes(self, user_id: int) -> Dict:
        """Verifica si el usuario puede agregar más fuentes según su plan"""
        connection = self.get_connection()
        if not connection:
            return {'puede_agregar': False, 'mensaje': 'Error de conexión'}
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Obtener suscripción activa
            suscripcion = self.obtener_suscripcion_activa(user_id)
            
            # ✅ SI NO HAY SUSCRIPCIÓN ACTIVA, USAR PLAN GRATUITO POR DEFECTO
            if not suscripcion:
                print(f"ℹ️ Usuario {user_id} sin suscripción activa, aplicando plan Gratuito por defecto")
                
                # Obtener plan gratuito de la base de datos
                cursor.execute("""
                    SELECT id, nombre, limite_fuentes, limite_scraping_diario
                    FROM planes 
                    WHERE nombre ILIKE '%gratis%' OR precio = 0
                    ORDER BY precio ASC
                    LIMIT 1
                """)
                plan_gratuito = cursor.fetchone()
                
                if plan_gratuito:
                    suscripcion = {
                        'plan_nombre': plan_gratuito['nombre'],
                        'limite_fuentes': plan_gratuito['limite_fuentes']
                    }
                    print(f"✅ Aplicando plan '{plan_gratuito['nombre']}' con límite de {plan_gratuito['limite_fuentes']} fuentes")
                else:
                    # Fallback: Plan gratuito hardcoded si no existe en BD
                    suscripcion = {
                        'plan_nombre': 'Gratis',
                        'limite_fuentes': 3
                    }
                    print(f"⚠️ Plan gratuito no encontrado en BD, usando límite por defecto: 3 fuentes")
            
            limite = suscripcion['limite_fuentes']
            plan_nombre = suscripcion['plan_nombre']
            
            # Si limite es -1, es ilimitado
            if limite == -1:
                return {
                    'puede_agregar': True,
                    'limite': -1,
                    'actuales': 0,
                    'plan': plan_nombre
                }
            
            # Contar fuentes actuales del usuario
            cursor.execute("SELECT COUNT(*) as total FROM fuentes WHERE user_id = %s", (user_id,))
            fuentes_actuales = cursor.fetchone()['total']
            
            puede_agregar = fuentes_actuales < limite
            
            return {
                'puede_agregar': puede_agregar,
                'limite': limite,
                'actuales': fuentes_actuales,
                'plan': plan_nombre,
                'mensaje': f'Tienes {fuentes_actuales} de {limite} fuentes. ' + 
                            ('Puedes agregar más.' if puede_agregar else 'Has alcanzado el límite de tu plan.')
            }
        except Exception as e:
            print(f"❌ Error verificando límite: {e}")
            import traceback
            traceback.print_exc()
            return {'puede_agregar': False, 'mensaje': 'Error verificando límite'}
        finally:
            cursor.close()
            connection.close()

    # ==================== OPERACIONES DE PAGOS ====================

    def crear_pago(self, user_id: int, plan_id: int, metodo_pago: str, monto: float, 
                   referencia_pago: Optional[str] = None, datos_pago: Optional[Dict] = None) -> Optional[Dict]:
        """Registra un nuevo pago"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                INSERT INTO pagos (user_id, plan_id, metodo_pago, monto, referencia_pago, datos_pago, estado)
                VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')
                RETURNING *
            """, (user_id, plan_id, metodo_pago, monto, referencia_pago, 
                  json.dumps(datos_pago) if datos_pago else None))
            
            pago = dict(cursor.fetchone())
            connection.commit()
            print(f"✅ Pago registrado: ID {pago['id']}")
            return pago
        except Exception as e:
            print(f"❌ Error creando pago: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()

    def actualizar_estado_pago(self, pago_id: int, estado: str, verificado_por: Optional[int] = None) -> bool:
        """Actualiza el estado de un pago"""
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                UPDATE pagos 
                SET estado = %s, 
                    fecha_verificacion = CURRENT_TIMESTAMP,
                    verificado_por = %s
                WHERE id = %s
            """, (estado, verificado_por, pago_id))
            
            connection.commit()
            print(f"✅ Pago {pago_id} actualizado a estado: {estado}")
            return True
        except Exception as e:
            print(f"❌ Error actualizando pago: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()

    def obtener_pago(self, pago_id: int) -> Optional[Dict]:
        """Obtiene un pago por ID"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT p.*, pl.nombre as plan_nombre, u.nombre_usuario
                FROM pagos p
                JOIN planes pl ON p.plan_id = pl.id
                JOIN usuarios u ON p.user_id = u.id
                WHERE p.id = %s
            """, (pago_id,))
            
            pago = cursor.fetchone()
            return dict(pago) if pago else None
        except Exception as e:
            print(f"❌ Error obteniendo pago: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    def obtener_pagos_usuario(self, user_id: int) -> List[Dict]:
        """Obtiene todos los pagos de un usuario"""
        connection = self.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT p.*, pl.nombre as plan_nombre
                FROM pagos p
                JOIN planes pl ON p.plan_id = pl.id
                WHERE p.user_id = %s
                ORDER BY p.fecha_pago DESC
            """, (user_id,))
            
            pagos = [dict(row) for row in cursor.fetchall()]
            return pagos
        except Exception as e:
            print(f"❌ Error obteniendo pagos: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def obtener_pago_por_referencia(self, referencia_pago: str) -> Optional[Dict]:
        """Obtiene un pago por su referencia externa (PayPal, Stripe, etc.)"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT p.*, pl.nombre as plan_nombre
                FROM pagos p
                JOIN planes pl ON p.plan_id = pl.id
                WHERE p.referencia_pago = %s
            """, (referencia_pago,))
            
            pago = cursor.fetchone()
            return dict(pago) if pago else None
        except Exception as e:
            print(f"❌ Error obteniendo pago por referencia: {e}")
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
        
        where_clauses = []
        params = []
        
        if not es_admin and user_id is not None:
            where_clauses.append("user_id = %s")
            params.append(int(user_id))
        
        if solo_activas:
            where_clauses.append("activo = TRUE")
        
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
            if es_admin:
                cursor.execute("SELECT * FROM fuentes WHERE id = %s", (fuente_id,))
            elif user_id is not None:
                cursor.execute("SELECT * FROM fuentes WHERE id = %s AND user_id = %s", (fuente_id, int(user_id)))
            else:
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
            INSERT INTO noticias (titulo, url, resumen, imagen_url, categoria, pais, fuente_id, user_id, fecha_publicacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url, user_id) DO UPDATE SET 
                titulo = EXCLUDED.titulo,
                resumen = EXCLUDED.resumen,
                imagen_url = EXCLUDED.imagen_url,
                categoria = EXCLUDED.categoria,
                pais = EXCLUDED.pais,
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
            noticia.get('pais'),
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
        pais: Optional[str] = None,
        user_id: Optional[int] = None,
        es_admin: bool = False
    ):
        """Obtiene noticias de la BD con paginación y filtros. Retorna (noticias, total)"""
        connection = self.get_connection()
        if not connection:
            return [], 0
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        where_clause = "WHERE 1=1"
        parametros = []
        
        if not es_admin and user_id is not None:
            where_clause += " AND n.user_id = %s"
            parametros.append(int(user_id))
        
        if fuente_id is not None:
            where_clause += " AND n.fuente_id = %s"
            parametros.append(int(fuente_id))
        
        if categoria:
            where_clause += " AND n.categoria = %s"
            parametros.append(categoria)
        
        if pais:
            where_clause += " AND n.pais = %s"
            parametros.append(pais)
        
        count_query = f"""
            SELECT COUNT(*) as total
            FROM noticias n
            LEFT JOIN fuentes f ON n.fuente_id = f.id
            {where_clause}
        """
        
        try:
            cursor.execute(count_query, parametros)
            total = cursor.fetchone()['total']
            
            query = f"""
                SELECT n.*, f.nombre as fuente_nombre
                FROM noticias n
                LEFT JOIN fuentes f ON n.fuente_id = f.id
                {where_clause}
                ORDER BY n.fecha_scraping DESC LIMIT %s OFFSET %s
            """
            query_params = parametros.copy()
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
    
    def obtener_paises(self, user_id: Optional[int] = None, es_admin: bool = False) -> List[str]:
        """Obtiene todos los países únicos de noticias (filtrado por usuario si no es admin)"""
        connection = self.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            query = """
                SELECT DISTINCT pais 
                FROM noticias 
                WHERE pais IS NOT NULL
            """
            params = []
            
            if not es_admin and user_id is not None:
                query += " AND user_id = %s"
                params.append(int(user_id))
            
            query += " ORDER BY pais"
            
            cursor.execute(query, params)
            paises = [row[0] for row in cursor.fetchall()]
            return paises
            
        except Exception as e:
            print(f"❌ Error obteniendo países: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    # ==================== OPERACIONES DE SCRAPING DIARIO ====================

    def obtener_scraping_hoy(self, user_id: int) -> Dict:
        """Obtiene el registro de scraping del usuario para hoy"""
        connection = self.get_connection()
        if not connection:
            return {'cantidad': 0, 'fecha': None}
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT * FROM scraping_diario 
                WHERE user_id = %s AND fecha = CURRENT_DATE
            """, (user_id,))
            
            registro = cursor.fetchone()
            return dict(registro) if registro else {'cantidad': 0, 'fecha': None}
        except Exception as e:
            print(f"❌ Error obteniendo scraping hoy: {e}")
            return {'cantidad': 0, 'fecha': None}
        finally:
            cursor.close()
            connection.close()

    def incrementar_scraping_diario(self, user_id: int, cantidad: int = 1) -> bool:
        """Incrementa el contador de scraping diario"""
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            # Obtener suscripción activa
            suscripcion = self.obtener_suscripcion_activa(user_id)
            plan_id = suscripcion['plan_id'] if suscripcion else None
            
            # Insertar o actualizar registro de hoy
            cursor.execute("""
                INSERT INTO scraping_diario (user_id, fecha, cantidad, plan_id)
                VALUES (%s, CURRENT_DATE, %s, %s)
                ON CONFLICT (user_id, fecha) 
                DO UPDATE SET 
                    cantidad = scraping_diario.cantidad + EXCLUDED.cantidad,
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """, (user_id, cantidad, plan_id))
            
            connection.commit()
            return True
        except Exception as e:
            print(f"❌ Error incrementando scraping: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()

    def verificar_limite_scraping(self, user_id: int, cantidad_a_scrapear: int = 1) -> Dict:
        """Verifica si el usuario puede hacer scraping según su plan"""
        connection = self.get_connection()
        if not connection:
            return {'puede_scrapear': False, 'mensaje': 'Error de conexión'}
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Obtener suscripción activa
            suscripcion = self.obtener_suscripcion_activa(user_id)
            
            # ✅ SI NO HAY SUSCRIPCIÓN ACTIVA, USAR PLAN GRATUITO POR DEFECTO
            if not suscripcion:
                print(f"ℹ️ Usuario {user_id} sin suscripción activa, aplicando plan Gratuito por defecto")
                
                # Obtener plan gratuito de la base de datos
                cursor.execute("""
                    SELECT id, nombre, limite_fuentes, limite_scraping_diario
                    FROM planes 
                    WHERE nombre ILIKE '%gratis%' OR precio = 0
                    ORDER BY precio ASC
                    LIMIT 1
                """)
                plan_gratuito = cursor.fetchone()
                
                if plan_gratuito:
                    suscripcion = {
                        'plan_nombre': plan_gratuito['nombre'],
                        'limite_scraping_diario': plan_gratuito['limite_scraping_diario']
                    }
                    print(f"✅ Aplicando plan '{plan_gratuito['nombre']}' con límite de {plan_gratuito['limite_scraping_diario']} scraping/día")
                else:
                    # Fallback: Plan gratuito hardcoded si no existe en BD
                    suscripcion = {
                        'plan_nombre': 'Gratis',
                        'limite_scraping_diario': 30
                    }
                    print(f"⚠️ Plan gratuito no encontrado en BD, usando límite por defecto: 30 scraping/día")
            
            limite = suscripcion['limite_scraping_diario']
            plan_nombre = suscripcion['plan_nombre']
            
            # Si limite es -1, es ilimitado
            if limite == -1:
                return {
                    'puede_scrapear': True,
                    'limite': -1,
                    'usado_hoy': 0,
                    'disponible': -1,
                    'plan': plan_nombre
                }
            
            # Obtener scraping de hoy
            scraping_hoy = self.obtener_scraping_hoy(user_id)
            usado_hoy = scraping_hoy.get('cantidad', 0)
            disponible = max(0, limite - usado_hoy)
            
            puede_scrapear = (usado_hoy + cantidad_a_scrapear) <= limite
            
            mensaje = f'Has usado {usado_hoy} de {limite} noticias hoy.'
            if puede_scrapear:
                mensaje += f' Disponibles: {disponible}'
            else:
                mensaje += ' ¡Límite diario alcanzado! Actualiza tu plan para más scraping.'
            
            return {
                'puede_scrapear': puede_scrapear,
                'limite': limite,
                'usado_hoy': usado_hoy,
                'disponible': disponible,
                'plan': plan_nombre,
                'mensaje': mensaje
            }
        except Exception as e:
            print(f"❌ Error verificando límite scraping: {e}")
            import traceback
            traceback.print_exc()
            return {'puede_scrapear': False, 'mensaje': f'Error verificando límite: {str(e)}'}
        finally:
            cursor.close()
            connection.close()

    def resetear_scraping_antiguo(self) -> bool:
        """Elimina registros de scraping antiguos (más de 30 días)"""
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM scraping_diario 
                WHERE fecha < CURRENT_DATE - INTERVAL '30 days'
            """)
            connection.commit()
            eliminados = cursor.rowcount
            if eliminados > 0:
                print(f"🧹 Limpiados {eliminados} registros antiguos de scraping")
            return True
        except Exception as e:
            print(f"❌ Error limpiando scraping antiguo: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()