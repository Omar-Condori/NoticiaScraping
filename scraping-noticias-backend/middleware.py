"""
Middleware para verificación de roles
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

