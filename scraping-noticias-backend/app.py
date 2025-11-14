from flask import Flask, jsonify, request, Response
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity  # <--- ¡NUEVO!
from scraper import NewsScraper
from scheduler import ScraperScheduler
from estadisticas import Estadisticas
from busqueda import BusquedaAvanzada
from exportar import Exportador
from auth import AuthManager  # <--- ¡NUEVO!
import json
from datetime import timedelta  # <--- ¡NUEVO!


# Inicializar Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para 

# <--- ¡NUEVA CONFIGURACIÓN! JWT
app.config['JWT_SECRET_KEY'] = 'tu-super-secreto-cambiar-en-produccion-2025'  # ⚠️ CAMBIA ESTO EN PRODUCCIÓN
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # Token válido por 24 horas
jwt = JWTManager(app)

# Inicializar scraper
scraper = NewsScraper()

# Inicializar nuevos módulos
scheduler = ScraperScheduler(scraper)
estadisticas_module = Estadisticas()
busqueda_module = BusquedaAvanzada()
exportador = Exportador()
auth_manager = AuthManager()  # <--- ¡NUEVO!

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
        'version': '3.0.0',  # <--- ¡ACTUALIZADO!
        'documentacion': f'http://localhost:8001{SWAGGER_URL}',
        'nuevas_funcionalidades': '⭐ JWT Authentication, Scheduler, Búsqueda Avanzada, Estadísticas, Exportación, Imágenes, Categorías',
        'endpoints': {
            'documentacion': '/docs',
            'autenticacion': {  # <--- ¡NUEVO!
                'registro': 'POST /api/v1/auth/register',
                'login': 'POST /api/v1/auth/login',
                'perfil': 'GET /api/v1/auth/perfil (requiere JWT)'
            },
            'scraping': {
                'scrapear_ahora': 'POST /api/v1/scraping/ejecutar (requiere JWT)',  # <--- ¡MODIFICADO!
                'scrapear_fuente': 'POST /api/v1/scraping/ejecutar?fuente_id=1 (requiere JWT)'
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
        
        # Validar campos requeridos
        if not datos or 'nombre_usuario' not in datos or 'email' not in datos or 'contrasena' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos',
                'campos_requeridos': ['nombre_usuario', 'email', 'contrasena']
            }), 400
        
        # Intentar registrar usuario
        resultado = auth_manager.registrar_usuario(
            nombre_usuario=datos['nombre_usuario'],
            email=datos['email'],
            contrasena=datos['contrasena']
        )
        
        if not resultado['success']:
            return jsonify({
                'error': resultado['error']
            }), 400
        
        # Generar token JWT automáticamente después del registro
        access_token = create_access_token(identity=resultado['usuario']['id'])
        
        return jsonify({
            'success': True,
            'mensaje': '✅ Usuario registrado exitosamente',
            'usuario': resultado['usuario'],
            'access_token': access_token
        }), 201
        
    except Exception as e:
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
        
        # Validar campos requeridos
        if not datos or 'nombre_usuario' not in datos or 'contrasena' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos',
                'campos_requeridos': ['nombre_usuario', 'contrasena']
            }), 400
        
        # Intentar autenticar usuario
        resultado = auth_manager.autenticar_usuario(
            nombre_usuario=datos['nombre_usuario'],
            contrasena=datos['contrasena']
        )
        
        if not resultado['success']:
            return jsonify({
                'error': resultado['error']
            }), 401
        
        # Generar token JWT
        access_token = create_access_token(identity=resultado['usuario']['id'])
        
        return jsonify({
            'success': True,
            'mensaje': '✅ Login exitoso',
            'usuario': resultado['usuario'],
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error en el login',
            'detalle': str(e)
        }), 500

@app.route('/api/v1/auth/perfil', methods=['GET'])
@jwt_required()  # <--- ¡PROTEGIDO! Requiere JWT válido
def obtener_perfil():
    """
    Obtiene el perfil del usuario autenticado
    
    Requiere: Authorization: Bearer <token>
    """
    try:
        # Obtener ID del usuario desde el token JWT
        usuario_id = get_jwt_identity()
        
        # Buscar usuario en la base de datos
        usuario = auth_manager.obtener_usuario_por_id(usuario_id)
        
        if not usuario:
            return jsonify({
                'error': 'Usuario no encontrado'
            }), 404
        
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
@jwt_required()  # <--- ¡PROTEGIDO! Requiere JWT válido
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
    # Obtener ID del usuario autenticado
    usuario_id = get_jwt_identity()
    print(f"🔐 Scraping ejecutado por usuario ID: {usuario_id}")
    
    limite = request.args.get('limite', default=5, type=int)
    fuente_id = request.args.get('fuente_id', type=int)
    guardar = request.args.get('guardar', default='true', type=str).lower() == 'true'
    
    try:
        if fuente_id:
            # Scrapear una fuente específica
            fuente = scraper.obtener_fuente(fuente_id)
            if not fuente:
                return jsonify({
                    'error': 'Fuente no encontrada',
                    'fuente_id': fuente_id
                }), 404
            
            noticias = scraper.scrape_fuente(fuente, limite, guardar)
            mensaje = f'Scraping completado de {fuente["nombre"]}'
        else:
            # Scrapear todas las fuentes activas
            noticias = scraper.scrape_todas_fuentes(limite, guardar)
            mensaje = 'Scraping completado de todas las fuentes'
        
        return jsonify({
            'success': True,
            'mensaje': mensaje,
            'total_noticias': len(noticias),
            'guardadas_en_bd': guardar,
            'usuario_id': usuario_id,  # <--- ¡NUEVO! Identificar quién ejecutó el scraping
            'noticias': noticias
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error ejecutando scraping',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE NOTICIAS ====================

@app.route('/api/v1/noticias', methods=['GET'])
def obtener_noticias():
    """
    Obtiene noticias guardadas en la base de datos con paginación
    
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
    
    try:
        noticias, total = scraper.obtener_noticias_guardadas(
            limite=limite,
            offset=offset,
            fuente_id=fuente_id,
            categoria=categoria
        )
        
        return jsonify({
            'success': True,
            'total': total,  # Total real de noticias que coinciden con los filtros
            'limite': limite,
            'offset': offset,
            'total_paginas': (total + limite - 1) // limite if limite > 0 else 0,  # Cálculo de páginas
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
def limpiar_noticias():
    """Elimina todas las noticias de la BD"""
    try:
        scraper.limpiar_noticias()
        return jsonify({
            'success': True,
            'mensaje': 'Todas las noticias han sido eliminadas'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Error limpiando noticias',
            'detalle': str(e)
        }), 500

# ==================== ENDPOINTS DE CATEGORIAS ====================

@app.route('/api/v1/categorias', methods=['GET'])
def obtener_categorias():
    """
    Obtiene todas las categorías únicas de noticias
    
    Retorna una lista de strings con las categorías disponibles
    """
    try:
        categorias = scraper.obtener_categorias()
        
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
def listar_fuentes():
    """Lista todas las fuentes configuradas"""
    solo_activas = request.args.get('activas', default='false', type=str).lower() == 'true'
    
    try:
        fuentes = scraper.obtener_fuentes(solo_activas=solo_activas)
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
def obtener_fuente(id):
    """Obtiene una fuente específica por ID"""
    try:
        fuente = scraper.obtener_fuente(id)
        if fuente:
            return jsonify({
                'success': True,
                'fuente': fuente
            }), 200
        else:
            return jsonify({
                'error': 'Fuente no encontrada',
                'fuente_id': id
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Error obteniendo fuente',
            'detalle': str(e)
        }), 500

# <--- ¡MODIFICACIÓN COMPLETA! Solo requiere nombre y url
@app.route('/api/v1/fuentes', methods=['POST'])
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
        datos = request.get_json()
        
        # <--- ¡MODIFICACIÓN! Solo validar nombre y url
        if 'nombre' not in datos or 'url' not in datos:
            return jsonify({
                'error': 'Faltan campos requeridos',
                'campos_requeridos': ['nombre', 'url'],
                'recibidos': list(datos.keys())
            }), 400
        
        # <--- ¡MEJORADO! Asignar valores por defecto más inteligentes a selectores opcionales
        # Intentar detectar el tipo de sitio y usar selectores más comunes
        url_lower = datos['url'].lower()
        
        # Selectores por defecto más comunes y flexibles
        selector_contenedor_default = {'name': 'article'}
        selector_titulo_default = {'name': 'h2'}
        selector_resumen_default = {'name': 'p'}
        selector_link_default = {'name': 'a'}
        selector_imagen_default = {'name': 'img'}  # El scraper buscará imágenes automáticamente
        selector_categoria_default = None  # Muchos sitios no tienen categoría visible
        
        # Si no se proporcionan selectores, usar los por defecto
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
        
        # Agregar fuente a la base de datos
        fuente = scraper.agregar_fuente(fuente_completa)
        
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
def actualizar_fuente(id):
    """
    Actualiza una fuente existente
    
    Body JSON (todos los campos son opcionales):
    {
        "nombre": "Nuevo nombre",
        "url": "https://nueva-url.com",
        "selector_contenedor": {"name": "div", "attrs": {"class": "noticia"}},
        "activo": false
    }
    """
    try:
        datos = request.get_json()
        fuente = scraper.actualizar_fuente(id, datos)
        
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
def eliminar_fuente(id):
    """Elimina una fuente"""
    try:
        resultado = scraper.eliminar_fuente(id)
        
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

@app.route('/api/v1/estadisticas', methods=['GET'])
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
    
    try:
        # Obtener noticias (retorna tupla: (noticias, total))
        noticias, total = scraper.obtener_noticias_guardadas(
            limite=limite,
            offset=0,
            fuente_id=fuente_id
        )
        
        if not noticias or len(noticias) == 0:
            return jsonify({
                'error': 'No hay noticias para exportar'
            }), 404
        
        # Exportar según formato
        if formato == 'csv':
            contenido = exportador.exportar_csv(noticias)
            mimetype = 'text/csv'
            extension = 'csv'
        elif formato == 'json':
            contenido = exportador.exportar_json(noticias)
            mimetype = 'application/json'
            extension = 'json'
        else:  # txt
            contenido = exportador.exportar_txt(noticias)
            mimetype = 'text/plain'
            extension = 'txt'
        
        # Crear respuesta con archivo descargable
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
        
        
# ==================== MANEJADORES DE ERRORES JWT ====================
# <--- ¡AQUÍ EMPIEZA EL BLOQUE AGREGADO!
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
# <--- ¡AQUÍ TERMINA EL BLOQUE AGREGADO!
        
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