from flask import Flask, jsonify, request, Response
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from scraper import NewsScraper
from scheduler import ScraperScheduler
from estadisticas import Estadisticas
from busqueda import BusquedaAvanzada
from exportar import Exportador
from auth import AuthManager
from payments import PaymentFactory, PaymentConfig
from middleware import admin_required, get_user_info, verificar_limite_fuentes, verificar_limite_scraping  # <--- MODIFICADO
import json
from datetime import timedelta


# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Configuración JWT
app.config['JWT_SECRET_KEY'] = 'tu-super-secreto-cambiar-en-produccion-2025'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# Inicializar scraper
scraper = NewsScraper()

# Inicializar nuevos módulos
scheduler = ScraperScheduler(scraper)
estadisticas_module = Estadisticas()
busqueda_module = BusquedaAvanzada()
exportador = Exportador()
auth_manager = AuthManager()

# Configuración de Swagger
SWAGGER_URL = '/docs'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "API Noticias - Scraping Backend"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# ==================== DOCUMENTACIÓN ====================

@app.route('/swagger.json')
def swagger_spec():
    """Sirve el archivo de especificación Swagger"""
    try:
        with open('swagger.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({'error': 'Archivo swagger.json no encontrado'}), 404

# ==================== ENDPOINTS PRINCIPALES ====================

@app.route('/')
def home():
    """Endpoint de bienvenida con información de la API"""
    return jsonify({
        'mensaje': '🚀 API de Scraping de Noticias con Autenticación JWT',
        'version': '3.0.0',
        'documentacion': f'http://localhost:8001{SWAGGER_URL}',
        'nuevas_funcionalidades': '⭐ JWT Authentication, Scheduler, Búsqueda Avanzada, Estadísticas, Exportación, Imágenes, Categorías, Planes y Pagos',
        'endpoints': {
            'documentacion': '/docs',
            'autenticacion': {
                'registro': 'POST /api/v1/auth/register',
                'login': 'POST /api/v1/auth/login',
                'perfil': 'GET /api/v1/auth/perfil (requiere JWT)'
            },
            'planes': {
                'listar': 'GET /api/v1/planes',
                'mi_plan': 'GET /api/v1/suscripciones/mi-plan (requiere JWT)',
                'cambiar_plan': 'POST /api/v1/suscripciones/cambiar (requiere JWT)'
            },
            'pagos': {
                'crear': 'POST /api/v1/pagos/crear (requiere JWT)',
                'mis_pagos': 'GET /api/v1/pagos/mis-pagos (requiere JWT)',
                'verificar_yape': 'POST /api/v1/pagos/verificar-yape (requiere JWT)'
            },
            'scraping': {
                'scrapear_ahora': 'POST /api/v1/scraping/ejecutar (requiere JWT)',
                'scrapear_fuente': 'POST /api/v1/scraping/ejecutar?fuente_id=1 (requiere JWT)',
                'estadisticas': 'GET /api/v1/scraping/estadisticas (requiere JWT)'
            },
            'scheduler': {
                'listar_tareas': 'GET /api/v1/scheduler/tareas',
                'crear_tarea': 'POST /api/v1/scheduler/tareas',
                'obtener_tarea': 'GET /api/v1/scheduler/tareas/{nombre}',
                'eliminar_tarea': 'DELETE /api/v1/scheduler/tareas/{nombre}',
                'pausar': 'POST /api/v1/scheduler/tareas/{nombre}/pausar',
                'reanudar': 'POST /api/v1/scheduler/tareas/{nombre}/reanudar'
            },
            'estadisticas': {
                'generales': 'GET /api/v1/estadisticas',
                'tendencias': 'GET /api/v1/estadisticas/tendencias?dias=7',
                'top_fuentes': 'GET /api/v1/estadisticas/top-fuentes?limite=5'
            },
            'busqueda': {
                'buscar': 'GET /api/v1/noticias/buscar?q=politica',
                'palabras_clave': 'POST /api/v1/noticias/buscar/palabras-clave'
            },
            'exportacion': {
                'exportar': 'GET /api/v1/noticias/exportar?formato=csv'
            },
            'noticias': {
                'listar_guardadas': 'GET /api/v1/noticias',
                'listar_con_paginacion': 'GET /api/v1/noticias?limite=20&offset=0',
                'filtrar_categoria': 'GET /api/v1/noticias?categoria=Política',
                'contar': 'GET /api/v1/noticias/contar',
                'limpiar': 'DELETE /api/v1/noticias'
            },
            'categorias': {
                'listar': 'GET /api/v1/categorias'
            },
            'fuentes': {
                'listar': 'GET /api/v1/fuentes',
                'crear': 'POST /api/v1/fuentes',
                'obtener': 'GET /api/v1/fuentes/{id}',
                'actualizar': 'PUT /api/v1/fuentes/{id}',
                'eliminar': 'DELETE /api/v1/fuentes/{id}'
            }
        },
        'nota_autenticacion': '🔐 Los endpoints protegidos requieren un token JWT en el header: Authorization: Bearer <token>'
    })


# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@app.route('/api/v1/auth/register', methods=['POST'])
def registrar_usuario():
    """
    Registra un nuevo usuario
    
    Body JSON requerido:
    {
        "nombre_usuario": "usuario123",
        "email": "usuario@ejemplo.com",
        "contrasena": "mipassword123"
    }
    """
    try:
        datos = request.get_json()
        
        print(f"📥 Datos recibidos en registro: {datos}")
        
        if not datos:
            return jsonify({
                'error': 'No se recibieron datos',
                'campos_requeridos': ['nombre_usuario', 'email', 'contrasena']
            }), 400
        
        if 'nombre_usuario' not in datos or 'email' not in datos or 'contrasena' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos',
                'campos_requeridos': ['nombre_usuario', 'email', 'contrasena'],
                'datos_recibidos': list(datos.keys()) if datos else []
            }), 400
        
        resultado = auth_manager.registrar_usuario(
            nombre_usuario=datos['nombre_usuario'],
            email=datos['email'],
            contrasena=datos['contrasena']
        )
        
        print(f"📤 Resultado del registro: {resultado}")
        
        if not resultado['success']:
            return jsonify({
                'error': resultado['error']
            }), 400
        
        usuario_respuesta = resultado['usuario'].copy()
        if 'rol' not in usuario_respuesta:
            usuario_respuesta['rol'] = 'usuario'
        
        access_token = create_access_token(
            identity=usuario_respuesta['id'],
            additional_claims={'rol': usuario_respuesta.get('rol', 'usuario')}
        )
        
        return jsonify({
            'success': True,
            'mensaje': '✅ Usuario registrado exitosamente',
            'usuario': usuario_respuesta,
            'access_token': access_token
        }), 201
        
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error en el registro',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login_usuario():
    """
    Inicia sesión y retorna un token JWT
    
    Body JSON requerido:
    {
        "nombre_usuario": "usuario123",
        "contrasena": "mipassword123"
    }
    """
    try:
        datos = request.get_json()
        
        print(f"📥 Datos recibidos en login: {datos}")
        
        if not datos:
            return jsonify({
                'error': 'No se recibieron datos',
                'campos_requeridos': ['nombre_usuario', 'contrasena']
            }), 400
        
        if 'nombre_usuario' not in datos or 'contrasena' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos',
                'campos_requeridos': ['nombre_usuario', 'contrasena'],
                'datos_recibidos': list(datos.keys()) if datos else []
            }), 400
        
        resultado = auth_manager.autenticar_usuario(
            nombre_usuario=datos['nombre_usuario'],
            contrasena=datos['contrasena']
        )
        
        print(f"📤 Resultado del login: {resultado}")
        
        if not resultado['success']:
            return jsonify({
                'error': resultado['error']
            }), 401
        
        usuario_respuesta = resultado['usuario'].copy()
        if 'rol' not in usuario_respuesta:
            usuario_respuesta['rol'] = 'usuario'
        
        access_token = create_access_token(
            identity=usuario_respuesta['id'],
            additional_claims={'rol': usuario_respuesta.get('rol', 'usuario')}
        )
        
        return jsonify({
            'success': True,
            'mensaje': '✅ Login exitoso',
            'usuario': usuario_respuesta,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error en el login',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/auth/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil():
    """
    Obtiene el perfil del usuario autenticado
    
    Requiere: Authorization: Bearer <token>
    """
    try:
        usuario_id = get_jwt_identity()
        
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        
        usuario = auth_manager.obtener_usuario_por_id(usuario_id)
        
        if not usuario:
            return jsonify({
                'error': 'Usuario no encontrado'
            }), 404
        
        usuario['rol'] = rol
        
        return jsonify({
            'success': True,
            'usuario': usuario
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo perfil',
            'detalle': str(e)
        }), 500



# ==================== ENDPOINTS DE SCRAPING ====================

@app.route('/api/v1/scraping/ejecutar', methods=['POST'])
@verificar_limite_scraping  # <--- MODIFICADO: Cambié de @jwt_required() a @verificar_limite_scraping
def ejecutar_scraping():
    """
    🔥 ENDPOINT PRINCIPAL: Ejecuta el scraping de noticias
    🔐 REQUIERE AUTENTICACIÓN JWT
    
    Header requerido:
        Authorization: Bearer <token>
    
    Query params opcionales:
        - limite: número de noticias por fuente (default: 5)
        - fuente_id: ID de fuente específica (opcional)
        - guardar: si debe guardar en BD (default: true)
    """
    usuario_id = get_jwt_identity()
    print(f"🔐 Scraping ejecutado por usuario ID: {usuario_id}")
    
    limite = request.args.get('limite', default=5, type=int)
    fuente_id = request.args.get('fuente_id', type=int)
    guardar = request.args.get('guardar', default='true', type=str).lower() == 'true'
    
    try:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
        
        if fuente_id:
            fuente = scraper.obtener_fuente(fuente_id, user_id=usuario_id, es_admin=es_admin)
            if not fuente:
                return jsonify({
                    'error': 'Fuente no encontrada o no tienes permiso para acceder a ella',
                    'fuente_id': fuente_id
                }), 404
            
            noticias = scraper.scrape_fuente(fuente, limite, guardar, usuario_id)
            mensaje = f'Scraping completado de {fuente["nombre"]}'
        else:
            noticias = scraper.scrape_todas_fuentes(limite, guardar, solo_activas=True, user_id=usuario_id)
            mensaje = 'Scraping completado de todas las fuentes'
        
        # <--- AGREGADO: Incrementar contador de scraping diario
        cantidad_scrapeada = len(noticias)
        if cantidad_scrapeada > 0:
            scraper.db.incrementar_scraping_diario(usuario_id, cantidad_scrapeada)
            print(f"📊 Contador actualizado: +{cantidad_scrapeada} noticias para usuario {usuario_id}")
        
        return jsonify({
            'success': True,
            'mensaje': mensaje,
            'total_noticias': len(noticias),
            'guardadas_en_bd': guardar,
            'usuario_id': usuario_id,
            'noticias': noticias
        }), 200
        
    except Exception as e:
        print(f"❌ Error en ejecutar_scraping: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error ejecutando scraping',
            'detalle': str(e)
        }), 500

# <--- AGREGADO: Nuevo endpoint de estadísticas de scraping
@app.route('/api/v1/scraping/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas_scraping():
    """Obtiene estadísticas de scraping del usuario"""
    try:
        usuario_id = get_jwt_identity()
        
        # Obtener info del plan
        suscripcion = scraper.db.obtener_suscripcion_activa(usuario_id)
        limite_info = scraper.db.verificar_limite_scraping(usuario_id)
        
        return jsonify({
            'success': True,
            'plan': suscripcion['plan_nombre'] if suscripcion else 'Sin plan',
            'limite_diario': limite_info.get('limite'),
            'usado_hoy': limite_info.get('usado_hoy'),
            'disponible': limite_info.get('disponible'),
            'puede_scrapear': limite_info.get('puede_scrapear'),
            'mensaje': limite_info.get('mensaje')
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({
            'error': 'Error obteniendo estadísticas',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE NOTICIAS ====================

@app.route('/api/v1/noticias', methods=['GET'])
@jwt_required(optional=True)
def obtener_noticias():
    """
    Obtiene noticias guardadas en la base de datos con paginación
    🔐 Si hay JWT, filtra por usuario. Admin ve todas.
    
    Query params:
        - limite: número máximo de noticias (default: 50)
        - offset: punto de inicio para paginación (default: 0)
        - fuente_id: ID de fuente específica (opcional)
        - categoria: filtrar por categoría (opcional)
    """
    limite = request.args.get('limite', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)
    fuente_id = request.args.get('fuente_id', type=int)
    categoria = request.args.get('categoria', type=str)
    
    usuario_id = None
    es_admin = False
    try:
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
    except:
        pass
    
    try:
        noticias, total = scraper.obtener_noticias_guardadas(
            limite=limite,
            offset=offset,
            fuente_id=fuente_id,
            categoria=categoria,
            user_id=usuario_id,
            es_admin=es_admin
        )
        
        return jsonify({
            'success': True,
            'total': total,
            'limite': limite,
            'offset': offset,
            'total_paginas': (total + limite - 1) // limite if limite > 0 else 0,
            'pagina_actual': (offset // limite) + 1 if limite > 0 else 1,
            'mensaje': 'Noticias obtenidas desde la base de datos',
            'noticias': noticias
        }), 200
        
    except Exception as e:
        print(f"❌ Error en GET /api/v1/noticias: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error obteniendo noticias',
            'detalle': str(e),
            'noticias': [],
            'total': 0
        }), 500

@app.route('/api/v1/noticias/contar', methods=['GET'])
def contar_noticias():
    """Cuenta el total de noticias en la BD"""
    try:
        total = scraper.contar_noticias()
        return jsonify({
            'success': True,
            'total_noticias': total
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Error contando noticias',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/noticias', methods=['DELETE'])
@jwt_required()
def limpiar_noticias():
    """Elimina noticias de la BD (del usuario autenticado o todas si es admin)"""
    try:
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
        
        scraper.limpiar_noticias(user_id=usuario_id, es_admin=es_admin)
        
        mensaje = 'Todas las noticias han sido eliminadas' if es_admin else 'Tus noticias han sido eliminadas'
        
        return jsonify({
            'success': True,
            'mensaje': mensaje
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Error limpiando noticias',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE CATEGORIAS ====================

@app.route('/api/v1/categorias', methods=['GET'])
@jwt_required(optional=True)
def obtener_categorias():
    """
    Obtiene todas las categorías únicas de noticias (filtrado por usuario si no es admin)
    
    Retorna una lista de strings con las categorías disponibles
    """
    usuario_id = None
    es_admin = False
    try:
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
    except:
        pass
    
    try:
        categorias = scraper.obtener_categorias(user_id=usuario_id, es_admin=es_admin)
        
        return jsonify({
            'success': True,
            'total': len(categorias),
            'categorias': categorias
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo categorías',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE FUENTES ====================

@app.route('/api/v1/fuentes', methods=['GET'])
@jwt_required(optional=True)
def listar_fuentes():
    """Lista fuentes configuradas (filtradas por usuario si no es admin)"""
    solo_activas = request.args.get('activas', default='false', type=str).lower() == 'true'
    
    usuario_id = None
    es_admin = False
    try:
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
    except:
        pass
    
    try:
        fuentes = scraper.obtener_fuentes(solo_activas=solo_activas, user_id=usuario_id, es_admin=es_admin)
        return jsonify({
            'success': True,
            'total': len(fuentes),
            'fuentes': fuentes or []
        }), 200
    except Exception as e:
        print(f"❌ Error en GET /api/v1/fuentes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error obteniendo fuentes',
            'detalle': str(e),
            'fuentes': [],
            'total': 0
        }), 500

@app.route('/api/v1/fuentes/<int:id>', methods=['GET'])
@jwt_required(optional=True)
def obtener_fuente(id):
    """Obtiene una fuente específica por ID (verifica que pertenezca al usuario si no es admin)"""
    usuario_id = None
    es_admin = False
    try:
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
    except:
        pass
    
    try:
        fuente = scraper.obtener_fuente(id, user_id=usuario_id, es_admin=es_admin)
        if fuente:
            return jsonify({
                'success': True,
                'fuente': fuente
            }), 200
        else:
            return jsonify({
                'error': 'Fuente no encontrada o no tienes permiso para acceder a ella',
                'fuente_id': id
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo fuente',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/fuentes', methods=['POST'])
@verificar_limite_fuentes
def agregar_fuente():
    """
    Agrega una nueva fuente (SIMPLIFICADO - Solo requiere nombre y url)
    
    Body JSON requerido:
    {
        "nombre": "Nombre del Sitio",
        "url": "https://ejemplo.com"
    }
    
    Los selectores son opcionales y se asignan automáticamente con valores por defecto.
    Si deseas personalizarlos, puedes incluir:
    - selector_contenedor
    - selector_titulo
    - selector_resumen
    - selector_link
    - selector_imagen
    - selector_categoria
    """
    try:
        usuario_id = get_jwt_identity()
        
        datos = request.get_json()
        
        if 'nombre' not in datos or 'url' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos',
                'campos_requeridos': ['nombre', 'url'],
                'recibidos': list(datos.keys())
            }), 400
        
        url_lower = datos['url'].lower()
        
        selector_contenedor_default = {'name': 'article'}
        selector_titulo_default = {'name': 'h2'}
        selector_resumen_default = {'name': 'p'}
        selector_link_default = {'name': 'a'}
        selector_imagen_default = {'name': 'img'}
        selector_categoria_default = None
        
        fuente_completa = {
            'nombre': datos['nombre'],
            'url': datos['url'],
            'selector_contenedor': datos.get('selector_contenedor') or selector_contenedor_default,
            'selector_titulo': datos.get('selector_titulo') or selector_titulo_default,
            'selector_resumen': datos.get('selector_resumen') or selector_resumen_default,
            'selector_link': datos.get('selector_link') or selector_link_default,
            'selector_imagen': datos.get('selector_imagen') or selector_imagen_default,
            'selector_categoria': datos.get('selector_categoria') or selector_categoria_default,
            'activo': datos.get('activo', True)
        }
        
        fuente = scraper.agregar_fuente(fuente_completa, usuario_id)
        
        if fuente:
            return jsonify({
                'success': True,
                'mensaje': '✅ Fuente agregada exitosamente con selectores por defecto',
                'info': 'La fuente usará selectores estándar HTML. Si no funciona, actualiza los selectores con PUT /api/v1/fuentes/{id}',
                'fuente': fuente
            }), 201
        else:
            return jsonify({
                'error': 'No se pudo agregar la fuente'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': 'Error agregando fuente',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/fuentes/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_fuente(id):
    """
    Actualiza una fuente existente (verifica que pertenezca al usuario si no es admin)
    
    Body JSON (todos los campos son opcionales):
    {
        "nombre": "Nuevo nombre",
        "url": "https://nueva-url.com",
        "selector_contenedor": {"name": "div", "attrs": {"class": "noticia"}},
        "activo": false
    }
    """
    try:
        usuario_id = get_jwt_identity()
        
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
        
        datos = request.get_json()
        fuente = scraper.actualizar_fuente(id, datos, user_id=usuario_id, es_admin=es_admin)
        
        if fuente:
            return jsonify({
                'success': True,
                'mensaje': 'Fuente actualizada exitosamente',
                'fuente': fuente
            }), 200
        else:
            return jsonify({
                'error': 'Fuente no encontrada',
                'fuente_id': id
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': 'Error actualizando fuente',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/fuentes/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_fuente(id):
    """Elimina una fuente (verifica que pertenezca al usuario si no es admin)"""
    try:
        usuario_id = get_jwt_identity()
        
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
        
        resultado = scraper.eliminar_fuente(id, user_id=usuario_id, es_admin=es_admin)
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': 'Fuente eliminada exitosamente',
                'fuente_id': id
            }), 200
        else:
            return jsonify({
                'error': 'Fuente no encontrada',
                'fuente_id': id
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': 'Error eliminando fuente',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE SCHEDULER ====================

@app.route('/api/v1/scheduler/tareas', methods=['GET'])
def listar_tareas_programadas():
    """Lista todas las tareas programadas"""
    try:
        tareas = scheduler.listar_tareas()
        return jsonify({
            'success': True,
            'total': len(tareas),
            'tareas': tareas
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Error listando tareas',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/scheduler/tareas', methods=['POST'])
def crear_tarea_programada():
    """
    Crea una nueva tarea programada
    
    Body JSON requerido:
    {
        "nombre": "scraping_diario",
        "intervalo_minutos": 60,
        "fuente_id": 1,
        "limite": 5
    }
    """
    try:
        datos = request.get_json()
        
        if 'nombre' not in datos or 'intervalo_minutos' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos: nombre, intervalo_minutos'
            }), 400
        
        resultado = scheduler.agregar_tarea(
            nombre=datos['nombre'],
            intervalo_minutos=datos['intervalo_minutos'],
            fuente_id=datos.get('fuente_id'),
            limite=datos.get('limite', 5)
        )
        
        if 'error' in resultado:
            return jsonify(resultado), 400
        
        return jsonify({
            'success': True,
            'mensaje': 'Tarea programada creada exitosamente',
            'tarea': resultado
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Error creando tarea',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/scheduler/tareas/<nombre>', methods=['GET'])
def obtener_tarea_programada(nombre):
    """Obtiene información de una tarea específica"""
    try:
        tarea = scheduler.obtener_tarea(nombre)
        if tarea:
            return jsonify({
                'success': True,
                'tarea': tarea
            }), 200
        else:
            return jsonify({
                'error': 'Tarea no encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo tarea',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/scheduler/tareas/<nombre>', methods=['DELETE'])
def eliminar_tarea_programada(nombre):
    """Elimina una tarea programada"""
    try:
        resultado = scheduler.eliminar_tarea(nombre)
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Tarea {nombre} eliminada'
            }), 200
        else:
            return jsonify({
                'error': 'Tarea no encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Error eliminando tarea',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/scheduler/tareas/<nombre>/pausar', methods=['POST'])
def pausar_tarea_programada(nombre):
    """Pausa una tarea programada"""
    try:
        resultado = scheduler.pausar_tarea(nombre)
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Tarea {nombre} pausada'
            }), 200
        else:
            return jsonify({
                'error': 'Tarea no encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Error pausando tarea',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/scheduler/tareas/<nombre>/reanudar', methods=['POST'])
def reanudar_tarea_programada(nombre):
    """Reanuda una tarea pausada"""
    try:
        resultado = scheduler.reanudar_tarea(nombre)
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Tarea {nombre} reanudada'
            }), 200
        else:
            return jsonify({
                'error': 'Tarea no encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Error reanudando tarea',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE ESTADÍSTICAS ====================

@app.route('/api/v1/scraping/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas generales del sistema"""
    try:
        stats = estadisticas_module.obtener_estadisticas_generales()
        return jsonify({
            'success': True,
            'estadisticas': stats
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo estadísticas',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/estadisticas/tendencias', methods=['GET'])
def obtener_tendencias():
    """
    Obtiene tendencias de scraping por día
    
    Query params:
        - dias: número de días atrás (default: 7)
    """
    dias = request.args.get('dias', default=7, type=int)
    
    try:
        tendencias = estadisticas_module.obtener_tendencias(dias)
        return jsonify({
            'success': True,
            'dias': dias,
            'tendencias': tendencias
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo tendencias',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/estadisticas/top-fuentes', methods=['GET'])
def obtener_top_fuentes():
    """
    Obtiene las fuentes con más noticias
    
    Query params:
        - limite: número de fuentes (default: 5)
    """
    limite = request.args.get('limite', default=5, type=int)
    
    try:
        top = estadisticas_module.obtener_top_fuentes(limite)
        return jsonify({
            'success': True,
            'top_fuentes': top
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo top fuentes',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE BÚSQUEDA ====================

@app.route('/api/v1/noticias/buscar', methods=['GET'])
def buscar_noticias():
    """
    Búsqueda avanzada de noticias
    
    Query params:
        - q: término de búsqueda
        - fuente_id: ID de fuente específica
        - fecha_desde: fecha desde (YYYY-MM-DD)
        - fecha_hasta: fecha hasta (YYYY-MM-DD)
        - limite: número máximo de resultados (default: 50)
        - orden: ASC o DESC (default: DESC)
    """
    query = request.args.get('q')
    fuente_id = request.args.get('fuente_id', type=int)
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    limite = request.args.get('limite', default=50, type=int)
    orden = request.args.get('orden', default='DESC', type=str)
    
    try:
        resultados = busqueda_module.buscar_noticias(
            query=query,
            fuente_id=fuente_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limite=limite,
            orden=orden
        )
        
        return jsonify({
            'success': True,
            'total': len(resultados),
            'parametros': {
                'query': query,
                'fuente_id': fuente_id,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'limite': limite,
                'orden': orden
            },
            'resultados': resultados
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error en búsqueda',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/noticias/buscar/palabras-clave', methods=['POST'])
def buscar_por_palabras_clave():
    """
    Busca noticias por múltiples palabras clave
    
    Body JSON:
    {
        "palabras": ["política", "economía", "tecnología"],
        "limite": 50
    }
    """
    try:
        datos = request.get_json()
        
        if 'palabras' not in datos:
            return jsonify({
                'error': 'Campo requerido: palabras (array)'
            }), 400
        
        resultados = busqueda_module.buscar_por_palabras_clave(
            palabras=datos['palabras'],
            limite=datos.get('limite', 50)
        )
        
        return jsonify({
            'success': True,
            'total': len(resultados),
            'palabras_buscadas': datos['palabras'],
            'resultados': resultados
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error en búsqueda por palabras clave',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE EXPORTACIÓN ====================

@app.route('/api/v1/noticias/exportar', methods=['GET'])
@jwt_required(optional=True)
def exportar_noticias():
    """
    Exporta noticias en diferentes formatos
    
    Query params:
        - formato: csv, json, txt (default: json)
        - limite: número de noticias (default: 100)
        - fuente_id: ID de fuente específica (opcional)
    """
    formato = request.args.get('formato', default='json', type=str).lower()
    limite = request.args.get('limite', default=100, type=int)
    fuente_id = request.args.get('fuente_id', type=int)
    
    if formato not in ['csv', 'json', 'txt']:
        return jsonify({
            'error': 'Formato no válido. Opciones: csv, json, txt'
        }), 400
    
    usuario_id = None
    es_admin = False
    try:
        usuario_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        es_admin = (rol == 'admin')
    except:
        pass
    
    try:
        noticias, total = scraper.obtener_noticias_guardadas(
            limite=limite,
            offset=0,
            fuente_id=fuente_id,
            user_id=usuario_id,
            es_admin=es_admin
        )
        
        if not noticias or len(noticias) == 0:
            return jsonify({
                'error': 'No hay noticias para exportar'
            }), 404
        
        if formato == 'csv':
            contenido = exportador.exportar_csv(noticias)
            mimetype = 'text/csv'
            extension = 'csv'
        elif formato == 'json':
            contenido = exportador.exportar_json(noticias)
            mimetype = 'application/json'
            extension = 'json'
        else:
            contenido = exportador.exportar_txt(noticias)
            mimetype = 'text/plain'
            extension = 'txt'
        
        return Response(
            contenido,
            mimetype=mimetype,
            headers={
                'Content-Disposition': f'attachment; filename=noticias.{extension}'
            }
        )
        
    except Exception as e:
        print(f"❌ Error en exportar_noticias: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error exportando noticias',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE PLANES ====================

@app.route('/api/v1/planes', methods=['GET'])
def obtener_planes():
    """
    Obtiene todos los planes disponibles
    
    No requiere autenticación
    """
    try:
        planes = scraper.db.obtener_planes()
        return jsonify({
            'success': True,
            'planes': planes
        }), 200
    except Exception as e:
        print(f"❌ Error obteniendo planes: {e}")
        return jsonify({
            'error': 'Error obteniendo planes',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE SUSCRIPCIONES ====================

@app.route('/api/v1/suscripciones/mi-plan', methods=['GET'])
@jwt_required()
def obtener_mi_plan():
    """
    Obtiene el plan actual del usuario autenticado
    
    Requiere: Authorization: Bearer <token>
    """
    try:
        usuario_id = get_jwt_identity()
        
        suscripcion = scraper.db.obtener_suscripcion_activa(usuario_id)
        
        if not suscripcion:
            return jsonify({
                'success': False,
                'error': 'No tienes una suscripción activa'
            }), 404
        
        limite_info = scraper.db.verificar_limite_fuentes(usuario_id)
        
        return jsonify({
            'success': True,
            'suscripcion': suscripcion,
            'limite_info': limite_info
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo plan: {e}")
        return jsonify({
            'error': 'Error obteniendo plan',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/suscripciones/cambiar', methods=['POST'])
@jwt_required()
def cambiar_plan():
    """
    Cambia el plan del usuario (después de un pago exitoso)
    
    Body JSON requerido:
    {
        "plan_id": 2,
        "pago_id": 123
    }
    """
    try:
        usuario_id = get_jwt_identity()
        datos = request.get_json()
        
        if 'plan_id' not in datos or 'pago_id' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos: plan_id, pago_id'
            }), 400
        
        pago = scraper.db.obtener_pago(datos['pago_id'])
        
        if not pago:
            return jsonify({
                'error': 'Pago no encontrado'
            }), 404
        
        if pago['estado'] != 'completado':
            return jsonify({
                'error': 'El pago no está completado',
                'estado': pago['estado']
            }), 400
        
        if pago['user_id'] != usuario_id:
            return jsonify({
                'error': 'Este pago no pertenece a tu usuario'
            }), 403
        
        suscripcion = scraper.db.crear_suscripcion(usuario_id, datos['plan_id'])
        
        if not suscripcion:
            return jsonify({
                'error': 'No se pudo crear la suscripción'
            }), 500
        
        return jsonify({
            'success': True,
            'mensaje': '✅ Plan actualizado exitosamente',
            'suscripcion': suscripcion
        }), 200
        
    except Exception as e:
        print(f"❌ Error cambiando plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error cambiando plan',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE PAGOS ====================

@app.route('/api/v1/pagos/crear', methods=['POST'])
@jwt_required()
def crear_pago():
    """
    Crea un pago para un plan
    
    Body JSON requerido:
    {
        "plan_id": 2,
        "metodo_pago": "yape" | "paypal" | "stripe"
    }
    """
    try:
        usuario_id = get_jwt_identity()
        datos = request.get_json()
        
        if 'plan_id' not in datos or 'metodo_pago' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos: plan_id, metodo_pago'
            }), 400
        
        plan_id = datos['plan_id']
        metodo_pago = datos['metodo_pago'].lower()
        
        if metodo_pago not in ['yape', 'paypal', 'stripe']:
            return jsonify({
                'error': 'Método de pago no válido. Opciones: yape, paypal, stripe'
            }), 400
        
        plan = scraper.db.obtener_plan(plan_id)
        if not plan:
            return jsonify({
                'error': 'Plan no encontrado'
            }), 404
        
        usuario = scraper.db.obtener_usuario_por_id(usuario_id)
        
        pago = scraper.db.crear_pago(
            user_id=usuario_id,
            plan_id=plan_id,
            metodo_pago=metodo_pago,
            monto=float(plan['precio'])
        )
        
        if not pago:
            return jsonify({
                'error': 'No se pudo registrar el pago'
            }), 500
        
        processor = PaymentFactory.get_processor(metodo_pago)
        
        if metodo_pago == 'yape':
            resultado = processor.generar_qr(
                monto=float(plan['precio']),
                plan_nombre=plan['nombre'],
                pago_id=pago['id']
            )
            
            return jsonify({
                'success': True,
                'metodo': 'yape',
                'pago_id': pago['id'],
                'qr_data': resultado
            }), 200
            
        elif metodo_pago == 'paypal':
            resultado = processor.crear_pago(
                monto=float(plan['precio']),
                plan_nombre=plan['nombre'],
                plan_id=plan_id,
                user_email=usuario['email']
            )
            
            if resultado.get('success'):
                scraper.db.actualizar_estado_pago(pago['id'], 'pendiente')
                
                return jsonify({
                    'success': True,
                    'metodo': 'paypal',
                    'pago_id': pago['id'],
                    'approval_url': resultado['approval_url'],
                    'payment_id': resultado['payment_id']
                }), 200
            else:
                return jsonify({
                    'error': 'Error creando pago PayPal',
                    'detalle': resultado.get('error')
                }), 500
                
        elif metodo_pago == 'stripe':
            resultado = processor.crear_sesion_checkout(
                monto=float(plan['precio']),
                plan_nombre=plan['nombre'],
                plan_id=plan_id,
                user_email=usuario['email'],
                pago_id=pago['id']
            )
            
            if resultado.get('success'):
                return jsonify({
                    'success': True,
                    'metodo': 'stripe',
                    'pago_id': pago['id'],
                    'checkout_url': resultado['checkout_url'],
                    'session_id': resultado['session_id']
                }), 200
            else:
                return jsonify({
                    'error': 'Error creando sesión Stripe',
                    'detalle': resultado.get('error')
                }), 500
        
    except Exception as e:
        print(f"❌ Error creando pago: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error creando pago',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/pagos/verificar-yape', methods=['POST'])
@jwt_required()
def verificar_pago_yape():
    """
    Verifica un pago de Yape (subir comprobante)
    
    Body JSON requerido:
    {
        "pago_id": 123,
        "comprobante_img": "base64..." (opcional)
    }
    """
    try:
        usuario_id = get_jwt_identity()
        datos = request.get_json()
        
        if 'pago_id' not in datos:
            return jsonify({
                'error': 'Falta campo requerido: pago_id'
            }), 400
        
        pago_id = datos['pago_id']
        
        pago = scraper.db.obtener_pago(pago_id)
        
        if not pago:
            return jsonify({
                'error': 'Pago no encontrado'
            }), 404
        
        if pago['user_id'] != usuario_id:
            return jsonify({
                'error': 'Este pago no pertenece a tu usuario'
            }), 403
        
        if pago['metodo_pago'] != 'yape':
            return jsonify({
                'error': 'Este pago no es de Yape'
            }), 400
        
        scraper.db.actualizar_estado_pago(pago_id, 'pendiente_verificacion')
        
        return jsonify({
            'success': True,
            'mensaje': 'Comprobante recibido. Un administrador verificará tu pago en las próximas 24 horas.',
            'pago_id': pago_id,
            'estado': 'pendiente_verificacion'
        }), 200
        
    except Exception as e:
        print(f"❌ Error verificando pago Yape: {e}")
        return jsonify({
            'error': 'Error verificando pago',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/pagos/webhook/paypal', methods=['POST'])
def webhook_paypal():
    """Webhook para recibir notificaciones de PayPal"""
    try:
        webhook_data = request.get_json()
        
        processor = PaymentFactory.get_processor('paypal')
        resultado = processor.verificar_webhook(webhook_data)
        
        if resultado.get('evento') == 'pago_completado':
            payment_id = resultado.get('payment_id')
            
            pago = scraper.db.obtener_pago_por_referencia(payment_id)
            
            if pago:
                scraper.db.actualizar_estado_pago(pago['id'], 'completado')
                scraper.db.crear_suscripcion(pago['user_id'], pago['plan_id'])
                print(f"✅ Pago PayPal completado: {payment_id}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"❌ Error en webhook PayPal: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/pagos/webhook/stripe', methods=['POST'])
def webhook_stripe():
    """Webhook para recibir notificaciones de Stripe"""
    try:
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        
        processor = PaymentFactory.get_processor('stripe')
        resultado = processor.verificar_webhook(payload, sig_header)
        
        if resultado.get('evento') == 'pago_completado':
            metadata = resultado.get('metadata', {})
            pago_id = metadata.get('pago_id')
            
            if pago_id:
                pago = scraper.db.obtener_pago(int(pago_id))
                
                if pago:
                    scraper.db.actualizar_estado_pago(pago['id'], 'completado')
                    scraper.db.crear_suscripcion(pago['user_id'], pago['plan_id'])
                    print(f"✅ Pago Stripe completado: {pago_id}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"❌ Error en webhook Stripe: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/pagos/mis-pagos', methods=['GET'])
@jwt_required()
def obtener_mis_pagos():
    """Obtiene el historial de pagos del usuario"""
    try:
        usuario_id = get_jwt_identity()
        pagos = scraper.db.obtener_pagos_usuario(usuario_id)
        
        return jsonify({
            'success': True,
            'pagos': pagos
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo pagos: {e}")
        return jsonify({
            'error': 'Error obteniendo pagos',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE ADMINISTRACIÓN ====================

@app.route('/api/v1/admin/pagos/pendientes', methods=['GET'])
@admin_required
def obtener_pagos_pendientes():
    """Obtiene todos los pagos pendientes de verificación (solo admin)"""
    try:
        from psycopg2.extras import RealDictCursor
        connection = scraper.db.get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT p.*, pl.nombre as plan_nombre, u.nombre_usuario, u.email
            FROM pagos p
            JOIN planes pl ON p.plan_id = pl.id
            JOIN usuarios u ON p.user_id = u.id
            WHERE p.estado = 'pendiente_verificacion'
            ORDER BY p.fecha_pago DESC
        """)
        
        pagos = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'pagos': pagos
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo pagos pendientes: {e}")
        return jsonify({
            'error': 'Error obteniendo pagos',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/admin/pagos/<int:pago_id>/aprobar', methods=['POST'])
@admin_required
def aprobar_pago(pago_id):
    """Aprueba manualmente un pago (solo admin)"""
    try:
        usuario_id = get_jwt_identity()
        
        pago = scraper.db.obtener_pago(pago_id)
        
        if not pago:
            return jsonify({
                'error': 'Pago no encontrado'
            }), 404
        
        scraper.db.actualizar_estado_pago(pago_id, 'completado', verificado_por=usuario_id)
        scraper.db.crear_suscripcion(pago['user_id'], pago['plan_id'])
        
        return jsonify({
            'success': True,
            'mensaje': 'Pago aprobado y suscripción activada'
        }), 200
        
    except Exception as e:
        print(f"❌ Error aprobando pago: {e}")
        return jsonify({
            'error': 'Error aprobando pago',
            'detalle': str(e)
        }), 500

# ==================== MANEJADORES DE ERRORES JWT ====================

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Maneja tokens expirados"""
    return jsonify({
        'error': 'Token expirado',
        'mensaje': 'El token JWT ha expirado. Por favor, inicia sesión nuevamente.'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Maneja tokens inválidos"""
    return jsonify({
        'error': 'Token inválido',
        'mensaje': 'El token JWT proporcionado es inválido.'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    """Maneja ausencia de token"""
    return jsonify({
        'error': 'Token requerido',
        'mensaje': 'Este endpoint requiere autenticación. Incluye el header: Authorization: Bearer <token>'
    }), 401

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'mensaje': 'Verifica la URL y el método HTTP'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'mensaje': str(error)
    }), 500

# ==================== INICIAR SERVIDOR ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 INICIANDO API DE SCRAPING DE NOTICIAS")
    print("="*60)
    print(f"📍 Servidor: http://localhost:8001")
    print(f"📖 Documentación: http://localhost:8001/docs")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8001)