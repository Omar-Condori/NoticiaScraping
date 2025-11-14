"""
Middleware para verificación de roles y límites
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

def admin_required(f):
    """Decorador que requiere rol de administrador"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        
        if rol != 'admin':
            return jsonify({
                'error': 'Acceso denegado. Se requiere rol de administrador.'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_info():
    """Obtiene información del usuario desde el token JWT"""
    try:
        usuario_id = get_jwt_identity()
        claims = get_jwt()
        rol = claims.get('rol', 'usuario')
        return {
            'id': usuario_id,
            'rol': rol,
            'es_admin': (rol == 'admin')
        }
    except:
        return None

def verificar_limite_fuentes(f):
    """
    Decorador que verifica si el usuario puede agregar más fuentes según su plan
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from database import Database
        
        usuario_id = get_jwt_identity()
        db = Database()
        
        # Verificar límite de fuentes
        resultado = db.verificar_limite_fuentes(usuario_id)
        
        if not resultado['puede_agregar']:
            # Obtener planes disponibles
            planes = db.obtener_planes()
            
            return jsonify({
                'error': 'Límite de fuentes alcanzado',
                'mensaje': resultado['mensaje'],
                'limite': resultado.get('limite'),
                'actuales': resultado.get('actuales'),
                'plan_actual': resultado.get('plan'),
                'planes_disponibles': planes,
                'accion_requerida': 'upgrade_plan'
            }), 403
        
        # Si puede agregar, continuar con la función
        return f(*args, **kwargs)
    return decorated_function

def verificar_limite_scraping(f):
    """
    Decorador que verifica si el usuario puede hacer scraping según su plan
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from database import Database
        from flask import request
        
        usuario_id = get_jwt_identity()
        db = Database()
        
        
        # Obtener cantidad de noticias a scrapear del request
        # Intentar obtener del body JSON, si falla usar query params
        try:
            datos = request.get_json(silent=True) or {}
            cantidad = datos.get('limite')
        except:
            datos = {}
            cantidad = None

        # Si no hay cantidad en el body, obtener de query params
        if cantidad is None:
            cantidad = request.args.get('limite', type=int, default=50) # Cantidad típica de scraping
        
        # Verificar límite de scraping
        resultado = db.verificar_limite_scraping(usuario_id, cantidad)
        
        if not resultado['puede_scrapear']:
            # Obtener planes disponibles
            planes = db.obtener_planes()
            
            return jsonify({
                'error': 'Límite de scraping diario alcanzado',
                'mensaje': resultado['mensaje'],
                'limite': resultado.get('limite'),
                'usado_hoy': resultado.get('usado_hoy'),
                'disponible': resultado.get('disponible'),
                'plan_actual': resultado.get('plan'),
                'planes_disponibles': planes,
                'accion_requerida': 'upgrade_plan'
            }), 403
        
        # Si puede scrapear, continuar con la función
        return f(*args, **kwargs)
    return decorated_function