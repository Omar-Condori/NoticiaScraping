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
            
            # Usuarios activos
            cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE activo = TRUE")
            usuarios_activos = cursor.fetchone()['total']
            
            # Total de suscripciones activas
            cursor.execute("SELECT COUNT(*) as total FROM suscripciones WHERE activo = TRUE")
            suscripciones_activas = cursor.fetchone()['total']
            
            # Total de pagos completados
            cursor.execute("SELECT COUNT(*) as total FROM pagos WHERE estado = 'completado'")
            pagos_completados = cursor.fetchone()['total']
            
            # Ingresos totales
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0) as total 
                FROM pagos 
                WHERE estado = 'completado'
            """)
            ingresos_totales = float(cursor.fetchone()['total'])
            
            # Ingresos del mes actual
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0) as total 
                FROM pagos 
                WHERE estado = 'completado'
                    AND DATE_TRUNC('month', fecha_pago) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            ingresos_mes = float(cursor.fetchone()['total'])
            
            # Usuarios registrados últimos 7 días (semana)
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM usuarios 
                WHERE fecha_creacion >= NOW() - INTERVAL '7 days'
            """)
            usuarios_semana = cursor.fetchone()['total']
            
            # Pagos pendientes
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM pagos 
                WHERE estado = 'pendiente'
            """)
            pagos_pendientes = cursor.fetchone()['total']
            
            cursor.close()
            connection.close()
            
            return {
                'usuarios': {
                    'total': total_usuarios,
                    'activos': usuarios_activos,
                    'semana': usuarios_semana
                },
                'ingresos': {
                    'total': ingresos_totales,
                    'mes_actual': ingresos_mes
                },
                'suscripciones': {
                    'activas': suscripciones_activas
                },
                'pagos': {
                    'completados': pagos_completados,
                    'pendientes': pagos_pendientes
                }
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo resumen: {e}")
            import traceback
            traceback.print_exc()
            return {
                'usuarios': {'total': 0, 'activos': 0, 'semana': 0},
                'ingresos': {'total': 0, 'mes_actual': 0},
                'suscripciones': {'activas': 0},
                'pagos': {'completados': 0, 'pendientes': 0}
            }
    
    def obtener_usuarios_por_plan(self):
        """Obtiene la distribución de usuarios por plan"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    p.nombre as plan,
                    COUNT(s.user_id) as total_usuarios,
                    COUNT(CASE WHEN s.activo = TRUE THEN 1 END) as activos,
                    p.precio
                FROM planes p
                LEFT JOIN suscripciones s ON p.id = s.plan_id
                GROUP BY p.id, p.nombre, p.precio
                ORDER BY p.precio ASC
            """)
            
            resultados = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo usuarios por plan: {e}")
            import traceback
            traceback.print_exc()
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
                WHERE estado = 'completado'
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
            import traceback
            traceback.print_exc()
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
                    u.fecha_creacion,
                    u.rol,
                    u.activo,
                    COALESCE(p.nombre, 'Sin plan') as plan
                FROM usuarios u
                LEFT JOIN suscripciones s ON u.id = s.user_id AND s.activo = TRUE
                LEFT JOIN planes p ON s.plan_id = p.id
                ORDER BY u.fecha_creacion DESC
                LIMIT %s
            """, (limite,))
            
            resultados = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo últimos usuarios: {e}")
            import traceback
            traceback.print_exc()
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
            import traceback
            traceback.print_exc()
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
                    pg.referencia_pago,
                    u.nombre_usuario,
                    u.email,
                    p.nombre as plan
                FROM pagos pg
                JOIN usuarios u ON pg.user_id = u.id
                JOIN planes p ON pg.plan_id = p.id
                WHERE pg.estado = 'pendiente'
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
            import traceback
            traceback.print_exc()
            return []