from database import Database

db = Database()

# 40 fuentes peruanas e internacionales
fuentes = [
    # Perú - Nacionales
    {'nombre': 'El Peruano', 'url': 'https://elperuano.pe/', 'user_id': 2},
    {'nombre': 'Trome', 'url': 'https://trome.pe/', 'user_id': 2},
    {'nombre': 'Ojo', 'url': 'https://ojo.pe/', 'user_id': 2},
    {'nombre': 'Depor', 'url': 'https://depor.com/', 'user_id': 2},
    {'nombre': 'La Prensa', 'url': 'https://laprensa.pe/', 'user_id': 2},
    {'nombre': 'Infobae Perú', 'url': 'https://www.infobae.com/peru/', 'user_id': 2},
    
    # Perú - Regionales
    {'nombre': 'RPP Arequipa', 'url': 'https://rpp.pe/lima', 'user_id': 2},
    {'nombre': 'El Búho', 'url': 'https://elbuho.pe/', 'user_id': 2},
    {'nombre': 'Wayka', 'url': 'https://wayka.pe/', 'user_id': 2},
    
    # Internacional - España
    {'nombre': 'El Mundo', 'url': 'https://www.elmundo.es/', 'user_id': 2},
    {'nombre': 'ABC España', 'url': 'https://www.abc.es/', 'user_id': 2},
    {'nombre': '20 Minutos', 'url': 'https://www.20minutos.es/', 'user_id': 2},
    
    # Internacional - Latinoamérica
    {'nombre': 'Clarín', 'url': 'https://www.clarin.com/', 'user_id': 2},
    {'nombre': 'La Nación', 'url': 'https://www.lanacion.com.ar/', 'user_id': 2},
    {'nombre': 'El Universal México', 'url': 'https://www.eluniversal.com.mx/', 'user_id': 2},
    {'nombre': 'El Tiempo Colombia', 'url': 'https://www.eltiempo.com/', 'user_id': 2},
    {'nombre': 'El Mercurio Chile', 'url': 'https://www.emol.com/', 'user_id': 2},
    
    # Internacional - Global
    {'nombre': 'Reuters', 'url': 'https://www.reuters.com/', 'user_id': 2},
    {'nombre': 'AP News', 'url': 'https://apnews.com/', 'user_id': 2},
    {'nombre': 'France 24', 'url': 'https://www.france24.com/es/', 'user_id': 2},
    {'nombre': 'DW Español', 'url': 'https://www.dw.com/es/', 'user_id': 2},
    {'nombre': 'Euronews', 'url': 'https://es.euronews.com/', 'user_id': 2},
    
    # Tecnología
    {'nombre': 'TechCrunch', 'url': 'https://techcrunch.com/', 'user_id': 2},
    {'nombre': 'The Verge', 'url': 'https://www.theverge.com/', 'user_id': 2},
    {'nombre': 'Xataka', 'url': 'https://www.xataka.com/', 'user_id': 2},
    
    # Deportes
    {'nombre': 'Marca', 'url': 'https://www.marca.com/', 'user_id': 2},
    {'nombre': 'AS', 'url': 'https://as.com/', 'user_id': 2},
    {'nombre': 'Goal', 'url': 'https://www.goal.com/es/', 'user_id': 2},
    
    # Economía
    {'nombre': 'Bloomberg', 'url': 'https://www.bloomberg.com/', 'user_id': 2},
    {'nombre': 'El Economista', 'url': 'https://www.eleconomista.com.mx/', 'user_id': 2},
]

# Selectores genéricos que funcionan en la mayoría de sitios
selector_generico = {
    'selector_contenedor': {'name': 'article'},
    'selector_titulo': {'name': 'h2'},
    'selector_resumen': {'name': 'p'},
    'selector_link': {'name': 'a'},
    'selector_imagen': {'name': 'img'},
    'selector_categoria': None,
    'activo': True
}

print("🚀 Agregando 30 fuentes nuevas...")
agregadas = 0

for fuente in fuentes:
    try:
        fuente_completa = {**fuente, **selector_generico}
        resultado = db.agregar_fuente(fuente_completa, fuente['user_id'])
        if resultado:
            agregadas += 1
            print(f"✅ {fuente['nombre']}")
    except Exception as e:
        print(f"❌ {fuente['nombre']}: {e}")

print(f"\n🎉 Total agregadas: {agregadas}/{len(fuentes)}")
