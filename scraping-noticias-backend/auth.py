"""
Módulo de Autenticación
Maneja la lógica de registro, login y validación de usuarios
"""
from database import Database
from typing import Optional, Dict

class AuthManager:
    def __init__(self):
        self.db = Database()
    
    def registrar_usuario(self, nombre_usuario: str, email: str, contrasena: str) -> Dict:
        """
        Registra un nuevo usuario
        
        Returns:
            Dict con 'success' y datos del usuario o 'error' con mensaje
        """
        # Validar que los campos no estén vacíos
        if not nombre_usuario or not email or not contrasena:
            return {
                'success': False,
                'error': 'Todos los campos son requeridos'
            }
        
        # Validar longitud mínima de contraseña
        if len(contrasena) < 6:
            return {
                'success': False,
                'error': 'La contraseña debe tener al menos 6 caracteres'
            }
        
        # Validar formato de email básico
        if '@' not in email or '.' not in email:
            return {
                'success': False,
                'error': 'Email inválido'
            }
        
        # Intentar crear el usuario
        resultado = self.db.crear_usuario(nombre_usuario, email, contrasena)
        
        if resultado is None:
            return {
                'success': False,
                'error': 'Error al crear usuario'
            }
        
        if isinstance(resultado, dict) and 'error' in resultado:
            if resultado['error'] == 'nombre_usuario_existe':
                return {
                    'success': False,
                    'error': 'El nombre de usuario ya está registrado'
                }
            elif resultado['error'] == 'email_existe':
                return {
                    'success': False,
                    'error': 'El email ya está registrado'
                }
            else:
                return {
                    'success': False,
                    'error': 'Error al crear usuario'
                }
        
        return {
            'success': True,
            'usuario': resultado
        }
    
    def autenticar_usuario(self, nombre_usuario: str, contrasena: str) -> Dict:
        """
        Autentica un usuario
        
        Returns:
            Dict con 'success' y datos del usuario o 'error' con mensaje
        """
        # Validar campos
        if not nombre_usuario or not contrasena:
            return {
                'success': False,
                'error': 'Nombre de usuario y contraseña son requeridos'
            }
        
        # Buscar usuario
        usuario = self.db.obtener_usuario_por_nombre(nombre_usuario)
        
        if not usuario:
            return {
                'success': False,
                'error': 'Credenciales inválidas'
            }
        
        # Verificar que el usuario esté activo
        if not usuario.get('activo', False):
            return {
                'success': False,
                'error': 'Usuario desactivado'
            }
        
        # Verificar contraseña
        if not self.db.verificar_contrasena(contrasena, usuario['contrasena_hash']):
            return {
                'success': False,
                'error': 'Credenciales inválidas'
            }
        
        # Remover contraseña hash de la respuesta
        usuario_seguro = {
            'id': usuario['id'],
            'nombre_usuario': usuario['nombre_usuario'],
            'email': usuario['email'],
            'fecha_creacion': str(usuario['fecha_creacion']),
            'activo': usuario['activo']
        }
        
        return {
            'success': True,
            'usuario': usuario_seguro
        }
    
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict]:
        """Obtiene información de un usuario por ID (sin contraseña)"""
        return self.db.obtener_usuario_por_id(usuario_id)