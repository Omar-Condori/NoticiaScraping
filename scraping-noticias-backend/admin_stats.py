# admin_stats.py
from database import Database
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor

class AdminStats:
    def __init__(self):
        self.db = Database()
    
    def obtener_resumen_general(self):
        """Obtiene un resumen general del sistema"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            # Total de usuarios
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cursor.fetchone()['total']
            
            # Total de noticias
            cursor.execute("SELECT COUNT(*) as total FROM noticias")
            total_noticias = cursor.fetchone()['total']
            
            # Total de fuentes
            cursor.execute("SELECT COUNT(*) as total FROM fuentes")
            total_fuentes = cursor.fetchone()['total']
            
            # Total de suscripciones activas
            cursor.execute("SELECT COUNT(*) as total FROM suscripciones WHERE activo = TRUE")
            suscripciones_activas = cursor.fetchone()['total']
            
            # Total de pagos completados
            cursor.execute("SELECT COUNT(*) as total FROM pagos WHERE estado = 'completado' OR estado = 'aprobado'")
            pagos_completados = cursor.fetchone()['total']
            
            # Ingresos totales
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0) as total 
                FROM pagos 
                WHERE estado = 'completado' OR estado = 'aprobado'
            """)
            ingresos_totales = float(cursor.fetchone()['total'])
            
            # Usuarios registrados últimos 30 días
            fecha_limite = datetime.now() - timedelta(days=30)
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM usuarios 
                WHERE fecha_registro >= %s
            """, (fecha_limite,))
            usuarios_nuevos = cursor.fetchone()['total']
            
            # Pagos pendientes
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM pagos 
                WHERE estado = 'pendiente_verificacion'
            """)
            pagos_pendientes = cursor.fetchone()['total']
            
            cursor.close()
            connection.close()
            
            return {
                'total_usuarios': total_usuarios,
                'total_noticias': total_noticias,
                'total_fuentes': total_fuentes,
                'suscripciones_activas': suscripciones_activas,
                'pagos_completados': pagos_completados,
                'ingresos_totales': ingresos_totales,
                'usuarios_nuevos_30d': usuarios_nuevos,
                'pagos_pendientes': pagos_pendientes
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo resumen: {e}")
            return {}
    
    def obtener_usuarios_por_plan(self):
        """Obtiene la distribución de usuarios por plan"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    p.nombre as plan,
                    COUNT(s.user_id) as total_usuarios,
                    p.precio
                FROM planes p
                LEFT JOIN suscripciones s ON p.id = s.plan_id AND s.activo = TRUE
                GROUP BY p.id, p.nombre, p.precio
                ORDER BY p.id
            """)
            
            resultados = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo usuarios por plan: {e}")
            return []
    
    def obtener_ingresos_mensuales(self, meses=6):
        """Obtiene los ingresos de los últimos N meses"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    TO_CHAR(fecha_pago, 'YYYY-MM') as mes,
                    COALESCE(SUM(monto), 0) as ingresos,
                    COUNT(*) as total_pagos
                FROM pagos
                WHERE (estado = 'completado' OR estado = 'aprobado')
                    AND fecha_pago >= NOW() - INTERVAL '%s months'
                GROUP BY TO_CHAR(fecha_pago, 'YYYY-MM')
                ORDER BY mes DESC
                LIMIT %s
            """, (meses, meses))
            
            resultados = [dict(row) for row in cursor.fetchall()]
            
            for resultado in resultados:
                resultado['ingresos'] = float(resultado['ingresos'])
            
            cursor.close()
            connection.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo ingresos mensuales: {e}")
            return []
    
    def obtener_ultimos_usuarios(self, limite=10):
        """Obtiene los últimos usuarios registrados"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    u.id,
                    u.nombre_usuario,
                    u.email,
                    u.fecha_registro,
                    u.rol,
                    COALESCE(p.nombre, 'Sin plan') as plan
                FROM usuarios u
                LEFT JOIN suscripciones s ON u.id = s.user_id AND s.activo = TRUE
                LEFT JOIN planes p ON s.plan_id = p.id
                ORDER BY u.fecha_registro DESC
                LIMIT %s
            """, (limite,))
            
            resultados = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo últimos usuarios: {e}")
            return []
    
    def obtener_pagos_recientes(self, limite=10):
        """Obtiene los pagos más recientes"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    pg.id,
                    pg.monto,
                    pg.metodo_pago,
                    pg.estado,
                    pg.fecha_pago,
                    u.nombre_usuario,
                    u.email,
                    p.nombre as plan
                FROM pagos pg
                JOIN usuarios u ON pg.user_id = u.id
                JOIN planes p ON pg.plan_id = p.id
                ORDER BY pg.fecha_pago DESC
                LIMIT %s
            """, (limite,))
            
            resultados = [dict(row) for row in cursor.fetchall()]
            
            for resultado in resultados:
                resultado['monto'] = float(resultado['monto'])
            
            cursor.close()
            connection.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo pagos recientes: {e}")
            return []
    
    def obtener_pagos_pendientes(self):
        """Obtiene todos los pagos pendientes de verificación"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    pg.id,
                    pg.monto,
                    pg.metodo_pago,
                    pg.estado,
                    pg.fecha_pago,
                    u.nombre_usuario,
                    u.email,
                    p.nombre as plan
                FROM pagos pg
                JOIN usuarios u ON pg.user_id = u.id
                JOIN planes p ON pg.plan_id = p.id
                WHERE pg.estado = 'pendiente_verificacion'
                ORDER BY pg.fecha_pago DESC
            """)
            
            resultados = [dict(row) for row in cursor.fetchall()]
            
            for resultado in resultados:
                resultado['monto'] = float(resultado['monto'])
            
            cursor.close()
            connection.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo pagos pendientes: {e}")
            return []