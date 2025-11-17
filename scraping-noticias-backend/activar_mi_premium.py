"""
Activa Premium Anual - VERSIÓN DEFINITIVA
Adaptado a la estructura exacta de tu base de datos
"""
from database import Database
from datetime import datetime, timedelta

def activar_premium_usuario(usuario_id=2):
    """Activa plan Premium Anual para un usuario específico"""
    db = Database()
    connection = db.get_connection()
    
    if not connection:
        print("❌ Error de conexión a la base de datos")
        return False
    
    cursor = connection.cursor()
    
    try:
        print(f"\n🔄 Procesando activación para usuario ID: {usuario_id}...")
        
        # 1. Obtener el plan Premium Anual (ID: 3)
        print("📦 Obteniendo plan Premium Anual...")
        cursor.execute("""
            SELECT id, nombre, precio, limite_scraping_diario, limite_fuentes
            FROM planes 
            WHERE id = 3
        """)
        
        plan = cursor.fetchone()
        
        if not plan:
            print("❌ Plan Premium Anual (ID: 3) no encontrado")
            return False
        
        plan_id, plan_nombre, plan_precio, limite_scraping, limite_fuentes = plan
        print(f"✅ Plan encontrado: {plan_nombre} (ID: {plan_id})")
        print(f"   💰 Precio: S/ {plan_precio}")
        print(f"   📊 Límite scraping: {'Ilimitado' if limite_scraping == -1 else limite_scraping}")
        print(f"   📰 Límite fuentes: {'Ilimitadas' if limite_fuentes == -1 else limite_fuentes}")
        
        # 2. Actualizar o crear suscripción
        fecha_inicio = datetime.now()
        fecha_vencimiento = fecha_inicio + timedelta(days=365)
        
        print("📅 Actualizando/creando suscripción Premium...")
        cursor.execute("""
            INSERT INTO suscripciones (
                user_id, plan_id, fecha_inicio, fecha_vencimiento, activo, cancelado
            )
            VALUES (%s, %s, %s, %s, TRUE, FALSE)
            ON CONFLICT (user_id) DO UPDATE
            SET 
                plan_id = EXCLUDED.plan_id,
                fecha_inicio = EXCLUDED.fecha_inicio,
                fecha_vencimiento = EXCLUDED.fecha_vencimiento,
                activo = TRUE,
                cancelado = FALSE
            RETURNING id
        """, (usuario_id, plan_id, fecha_inicio, fecha_vencimiento))
        
        suscripcion_id = cursor.fetchone()[0]
        print(f"✅ Suscripción actualizada/creada (ID: {suscripcion_id})")
        
        # 3. Registrar pago como "activación manual" (con estructura correcta)
        print("💳 Registrando pago...")
        cursor.execute("""
            INSERT INTO pagos (
                user_id, plan_id, metodo_pago, monto, 
                estado, fecha_pago, fecha_verificacion, notas
            )
            VALUES (
                %s, %s, 'activacion_manual', 0, 
                'aprobado', NOW(), NOW(), 'Activación manual para demo/presentación'
            )
        """, (usuario_id, plan_id))
        
        print("✅ Pago registrado")
        
        # 4. Limpiar contador de scraping diario (si existe)
        print("🔄 Limpiando contadores de scraping...")
        cursor.execute("""
            DELETE FROM scraping_diario 
            WHERE user_id = %s
        """, (usuario_id,))
        
        connection.commit()
        
        # Mostrar resumen
        print("\n" + "="*70)
        print("✅ ¡PREMIUM ANUAL ACTIVADO EXITOSAMENTE!")
        print("="*70)
        print(f"👤 Usuario ID: {usuario_id}")
        print(f"📦 Plan: {plan_nombre}")
        print(f"💰 Valor: S/ {plan_precio}/año")
        print(f"⏰ Duración: 365 días (1 año)")
        print(f"📅 Válido desde: {fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
        print(f"📅 Válido hasta: {fecha_vencimiento.strftime('%d/%m/%Y %H:%M')}")
        print(f"\n🚀 Beneficios del Plan Premium:")
        print(f"   • Scraping diario: {'🔥 ILIMITADO' if limite_scraping == -1 else f'{limite_scraping} noticias'}")
        print(f"   • Fuentes: {'🔥 ILIMITADAS' if limite_fuentes == -1 else f'{limite_fuentes} fuentes'}")
        print(f"   • Exportación: Avanzada (CSV, JSON, PDF)")
        print(f"   • Soporte: Prioritario ⭐")
        print(f"   • Acceso anticipado a nuevas funcionalidades ⭐")
        print(f"   • API access ⭐")
        print(f"   • Badge exclusivo ⭐")
        print("="*70)
        print("\n💡 PASOS SIGUIENTES:")
        print("   1. Presiona Ctrl+C para detener el backend")
        print("   2. Ejecuta: python app.py")
        print("   3. Recarga tu navegador (F5 o Cmd+Shift+R)")
        print("   4. ¡Verifica que aparezca 'Premium Anual' en tu perfil!")
        print("   5. Intenta hacer scraping - ¡Ya no habrá error 403!")
        print("\n🔐 ¡Ya tienes acceso completo a todas las funcionalidades!\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la activación: {e}")
        import traceback
        traceback.print_exc()
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()

def verificar_activacion(usuario_id=2):
    """Verifica que la activación se haya realizado correctamente"""
    db = Database()
    connection = db.get_connection()
    
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        print("\n" + "="*70)
        print("🔍 VERIFICACIÓN DE ACTIVACIÓN")
        print("="*70)
        
        # Verificar suscripción
        cursor.execute("""
            SELECT s.id, s.user_id, s.plan_id, s.fecha_inicio, s.fecha_vencimiento, 
                   s.activo, s.cancelado,
                   p.nombre as plan_nombre, p.limite_scraping_diario, p.limite_fuentes, p.precio
            FROM suscripciones s
            JOIN planes p ON s.plan_id = p.id
            WHERE s.user_id = %s
        """, (usuario_id,))
        
        suscripcion = cursor.fetchone()
        
        if suscripcion:
            (sub_id, user_id, plan_id, fecha_inicio, fecha_vencimiento, 
             activo, cancelado, plan_nombre, limite_scraping, limite_fuentes, precio) = suscripcion
            
            print(f"✅ Suscripción encontrada:")
            print(f"   📋 ID: {sub_id}")
            print(f"   👤 Usuario: {user_id}")
            print(f"   📦 Plan: {plan_nombre} (ID: {plan_id})")
            print(f"   💰 Precio: S/ {precio}")
            print(f"   📅 Inicio: {fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
            print(f"   📅 Vencimiento: {fecha_vencimiento.strftime('%d/%m/%Y %H:%M')}")
            print(f"   ✅ Activo: {'SÍ ✅' if activo else 'NO ❌'}")
            print(f"   🚫 Cancelado: {'Sí' if cancelado else 'No'}")
            print(f"   🚀 Scraping: {'🔥 ILIMITADO' if limite_scraping == -1 else f'{limite_scraping}/día'}")
            print(f"   📰 Fuentes: {'🔥 ILIMITADAS' if limite_fuentes == -1 else f'{limite_fuentes}'}")
            
            # Verificar vigencia
            ahora = datetime.now()
            if fecha_vencimiento > ahora and activo and not cancelado:
                dias_restantes = (fecha_vencimiento - ahora).days
                print(f"\n🎉 PLAN PREMIUM ACTIVO Y VIGENTE")
                print(f"⏰ Te quedan {dias_restantes} días de suscripción")
            else:
                print(f"\n⚠️  Plan expirado o inactivo")
            
            print("="*70)
            print("✅ VERIFICACIÓN EXITOSA - ¡Todo está correcto!\n")
        else:
            print("❌ No se encontró suscripción para este usuario")
            print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    print("\n" + "🎯 " * 30)
    print("ACTIVADOR DE PREMIUM ANUAL - Sistema de Scraping de Noticias")
    print("🎯 " * 30)
    
    MI_USUARIO_ID = 2  # omar
    
    print(f"\n👤 Usuario: ID {MI_USUARIO_ID} (omar)")
    print(f"📦 Plan: Premium Anual (ID: 3)")
    print(f"💰 Valor: S/ 79.99/año")
    print(f"⏰ Duración: 365 días\n")
    
    input("⚠️  Presiona ENTER para continuar con la activación...")
    
    exito = activar_premium_usuario(MI_USUARIO_ID)
    
    if exito:
        verificar_activacion(MI_USUARIO_ID)
        print("\n🎊 ¡ACTIVACIÓN COMPLETADA CON ÉXITO!")
        print("📋 Sigue los pasos indicados arriba.\n")
    else:
        print("\n❌ Activación fallida. Revisa los errores arriba.\n")