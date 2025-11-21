"""
Script para ejecutar scraping histórico
PROCESO SEPARADO - No afecta el scraping normal
"""
from scraper import NewsScraper
from scraping_historico import ScrapingHistorico

# ✅ CONFIGURACIÓN
USUARIO_ID = 2  # ← CAMBIAR a tu ID de usuario Premium Anual

DIAS_DESDE = 20  # Scrapear desde hace 20 días
DIAS_HASTA = 3   # Hasta hace 3 días (evita duplicar los últimos 3 días)
URLS_POR_FUENTE = 300  # Máximo de URLs por fuente

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🕒 SCRAPING HISTÓRICO MASIVO")
    print("="*70)
    print(f"\n⚙️  CONFIGURACIÓN:")
    print(f"   • Usuario ID: {USUARIO_ID}")
    print(f"   • Rango: Hace {DIAS_DESDE} días → Hace {DIAS_HASTA} días")
    print(f"   • URLs máximas por fuente: {URLS_POR_FUENTE}")
    print(f"\n✅ ESTO NO AFECTA EL SCRAPING NORMAL")
    print(f"✅ EVITA DUPLICADOS (últimos {DIAS_HASTA} días no se tocan)\n")
    
    # Inicializar
    scraper = NewsScraper()
    historico = ScrapingHistorico(scraper.db, scraper)
    
    # Obtener fuentes del usuario
    fuentes = scraper.obtener_fuentes(solo_activas=True, user_id=USUARIO_ID, es_admin=False)
    
    print(f"📋 Fuentes a procesar: {len(fuentes)}")
    print(f"📈 Noticias estimadas: {len(fuentes) * URLS_POR_FUENTE * 0.7:.0f}\n")
    
    respuesta = input("⏸️  ¿Continuar? (s/n): ")
    if respuesta.lower() != 's':
        print("❌ Cancelado")
        exit()
    
    # Estadísticas globales
    total_guardadas = 0
    total_duplicadas = 0
    total_errores = 0
    
    # Procesar cada fuente
    for idx, fuente in enumerate(fuentes, 1):
        print(f"\n{'='*70}")
        print(f"[{idx}/{len(fuentes)}] {fuente['nombre']}")
        print(f"{'='*70}")
        
        resultado = historico.scraping_historico_fuente(
            fuente=fuente,
            dias_desde=DIAS_DESDE,
            dias_hasta=DIAS_HASTA,
            limite_urls=URLS_POR_FUENTE,
            user_id=USUARIO_ID
        )
        
        if resultado['success']:
            total_guardadas += resultado['guardadas']
            total_duplicadas += resultado['ya_existian']
            total_errores += resultado['errores']
        
        print(f"📊 PROGRESO TOTAL:")
        print(f"   ✅ {total_guardadas} noticias nuevas")
        print(f"   ⏭️  {total_duplicadas} duplicadas (evitadas)")
        print(f"   ❌ {total_errores} errores")
    
    print("\n" + "="*70)
    print("✅ SCRAPING HISTÓRICO COMPLETADO")
    print("="*70)
    print(f"📈 RESUMEN FINAL:")
    print(f"   • Fuentes procesadas: {len(fuentes)}")
    print(f"   • Noticias nuevas guardadas: {total_guardadas}")
    print(f"   • Duplicadas evitadas: {total_duplicadas}")
    print(f"   • Errores: {total_errores}")
    print("="*70 + "\n")
