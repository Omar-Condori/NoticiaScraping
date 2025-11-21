from database import Database
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class Estadisticas:
    def __init__(self):
        self.db = Database()
    
    def obtener_estadisticas_generales(self, user_id: Optional[int] = None, es_admin: bool = False) -> Dict:
        """
        Obtiene estadísticas generales del sistema
        Si user_id es None o es_admin es True, muestra stats globales
        Si user_id está presente y no es admin, filtra por usuario
        """
        connection = self.db.get_connection()
        if not connection:
            return {}
        
        cursor = connection.cursor()
        
        try:
            # Determinar si filtrar por usuario
            filtro_usuario = "" if es_admin or user_id is None else f"WHERE n.user_id = {user_id}"
            filtro_fuentes = "" if es_admin or user_id is None else f"WHERE user_id = {user_id}"
            
            # Total de noticias
            cursor.execute(f"SELECT COUNT(*) FROM noticias n {filtro_usuario}")
            total_noticias = cursor.fetchone()[0]
            
            # Total de fuentes (del usuario o todas si es admin)
            cursor.execute(f"SELECT COUNT(*) FROM fuentes {filtro_fuentes}")
            total_fuentes = cursor.fetchone()[0]
            
            # Fuentes activas
            cursor.execute(f"""
                SELECT COUNT(*) FROM fuentes 
                WHERE activo = TRUE {('AND user_id = %s' if not es_admin and user_id else '')}
            """, (user_id,) if not es_admin and user_id else ())
            fuentes_activas = cursor.fetchone()[0]
            
            # Noticias por fuente
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT f.nombre, COUNT(n.id) as total
                    FROM fuentes f
                    LEFT JOIN noticias n ON f.id = n.fuente_id
                    GROUP BY f.id, f.nombre
                    ORDER BY total DESC
                """)
            else:
                cursor.execute("""
                    SELECT f.nombre, COUNT(n.id) as total
                    FROM fuentes f
                    LEFT JOIN noticias n ON f.id = n.fuente_id AND n.user_id = %s
                    WHERE f.user_id = %s
                    GROUP BY f.id, f.nombre
                    ORDER BY total DESC
                """, (user_id, user_id))
            
            noticias_por_fuente = [
                {'fuente': row[0], 'total': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Noticias de las últimas 24 horas
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '24 hours'
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '24 hours'
                    AND user_id = %s
                """, (user_id,))
            noticias_24h = cursor.fetchone()[0]
            
            # Noticias de la última semana
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '7 days'
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE fecha_scraping >= NOW() - INTERVAL '7 days'
                    AND user_id = %s
                """, (user_id,))
            noticias_semana = cursor.fetchone()[0]
            
            # Última noticia scrapeada
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT titulo, fecha_scraping 
                    FROM noticias 
                    ORDER BY fecha_scraping DESC 
                    LIMIT 1
                """)
            else:
                cursor.execute("""
                    SELECT titulo, fecha_scraping 
                    FROM noticias 
                    WHERE user_id = %s
                    ORDER BY fecha_scraping DESC 
                    LIMIT 1
                """, (user_id,))
            ultima_noticia = cursor.fetchone()
            
            return {
                'resumen': {
                    'total_noticias': total_noticias,
                    'total_fuentes': total_fuentes,
                    'fuentes_activas': fuentes_activas,
                    'noticias_24h': noticias_24h,
                    'noticias_semana': noticias_semana
                },
                'por_fuente': noticias_por_fuente,
                'ultima_actualizacion': {
                    'titulo': ultima_noticia[0] if ultima_noticia else None,
                    'fecha': str(ultima_noticia[1]) if ultima_noticia else None
                }
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            import traceback
            traceback.print_exc()
            return {}
        finally:
            cursor.close()
            connection.close()
    
    def obtener_tendencias(self, dias: int = 7, user_id: Optional[int] = None, es_admin: bool = False) -> List[Dict]:
        """Obtiene tendencias de scraping por día (filtradas por usuario si no es admin)"""
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT 
                        DATE(fecha_scraping) as fecha,
                        COUNT(*) as total_noticias
                    FROM noticias
                    WHERE fecha_scraping >= NOW() - INTERVAL '%s days'
                    GROUP BY DATE(fecha_scraping)
                    ORDER BY fecha DESC
                """, (dias,))
            else:
                cursor.execute("""
                    SELECT 
                        DATE(fecha_scraping) as fecha,
                        COUNT(*) as total_noticias
                    FROM noticias
                    WHERE fecha_scraping >= NOW() - INTERVAL '%s days'
                    AND user_id = %s
                    GROUP BY DATE(fecha_scraping)
                    ORDER BY fecha DESC
                """, (dias, user_id))
            
            tendencias = [
                {'fecha': str(row[0]), 'total': row[1]}
                for row in cursor.fetchall()
            ]
            
            return tendencias
            
        except Exception as e:
            print(f"❌ Error obteniendo tendencias: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            connection.close()
    
    def obtener_top_fuentes(self, limite: int = 5, user_id: Optional[int] = None, es_admin: bool = False) -> List[Dict]:
        """Obtiene las fuentes con más noticias (filtradas por usuario si no es admin)"""
        connection = self.db.get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        try:
            if es_admin or user_id is None:
                cursor.execute("""
                    SELECT 
                        f.nombre,
                        f.url,
                        COUNT(n.id) as total_noticias,
                        MAX(n.fecha_scraping) as ultima_actualizacion
                    FROM fuentes f
                    LEFT JOIN noticias n ON f.id = n.fuente_id
                    GROUP BY f.id, f.nombre, f.url
                    ORDER BY total_noticias DESC
                    LIMIT %s
                """, (limite,))
            else:
                cursor.execute("""
                    SELECT 
                        f.nombre,
                        f.url,
                        COUNT(n.id) as total_noticias,
                        MAX(n.fecha_scraping) as ultima_actualizacion
                    FROM fuentes f
                    LEFT JOIN noticias n ON f.id = n.fuente_id AND n.user_id = %s
                    WHERE f.user_id = %s
                    GROUP BY f.id, f.nombre, f.url
                    ORDER BY total_noticias DESC
                    LIMIT %s
                """, (user_id, user_id, limite))
            
            top_fuentes = [
                {
                    'nombre': row[0],
                    'url': row[1],
                    'total_noticias': row[2],
                    'ultima_actualizacion': str(row[3]) if row[3] else None
                }
                for row in cursor.fetchall()
            ]
            
            return top_fuentes
            
        except Exception as e:
            print(f"❌ Error obteniendo top fuentes: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            connection.close()
    def _log(self, msg):
        try:
            with open('/tmp/dashboard_debug.log', 'a') as f:
                f.write(f"{datetime.now()}: {msg}\n")
        except:
            pass

    def _analizar_sentimiento(self, texto: str) -> float:
        """
        Analiza el sentimiento de un texto usando un diccionario simple.
        Retorna un valor entre -1 (Negativo) y 1 (Positivo).
        """
        if not texto:
            return 0.0
            
        texto = texto.lower()
        
        positivas = {
            'bueno', 'excelente', 'gran', 'mejor', 'positivo', 'crecimiento', 'aumento', 
            'ganancia', 'éxito', 'logro', 'avance', 'supera', 'récord', 'beneficio', 
            'oportunidad', 'favorable', 'aprobado', 'seguro', 'confianza', 'alza',
            'recuperación', 'solución', 'acuerdo', 'paz', 'victoria', 'feliz', 'celebra'
        }
        
        negativas = {
            'malo', 'peor', 'negativo', 'caída', 'pérdida', 'crisis', 'riesgo', 
            'amenaza', 'error', 'fracaso', 'problema', 'dificultad', 'baja', 
            'desempleo', 'inflación', 'muerte', 'accidente', 'tragedia', 'conflicto',
            'guerra', 'violencia', 'crimen', 'robo', 'fraude', 'corrupción', 'ilegal',
            'denuncia', 'cierre', 'quiebra', 'deuda', 'déficit', 'retraso', 'peligro'
        }
        
        score = 0
        palabras = texto.split()
        total_palabras_clave = 0
        
        for palabra in palabras:
            # Limpiar puntuación
            palabra = palabra.strip('.,;:()[]{}"\'')
            if palabra in positivas:
                score += 1
                total_palabras_clave += 1
            elif palabra in negativas:
                score -= 1
                total_palabras_clave += 1
                
        if total_palabras_clave == 0:
            return 0.0
            
        return score / total_palabras_clave

    def obtener_datos_ia(self, user_id: int, cursor=None) -> Dict:
        """
        Genera datos para el Centro de Predicción e IA.
        Si se pasa cursor, se reutiliza. Si no, se crea nueva conexión.
        """
        self._log(f"Obteniendo datos IA para user_id={user_id}")
        connection = None
        should_close = False
        
        try:
            if cursor is None:
                connection = self.db.get_connection()
                if not connection:
                    self._log("Error: No hay conexión DB en obtener_datos_ia")
                    return {}
                cursor = connection.cursor()
                should_close = True
            
            # 1. Predicción de Tendencias (Momentum de Categoría)
            # Contar noticias por categoría HOY
            cursor.execute("""
                SELECT categoria, COUNT(*) FROM noticias 
                WHERE user_id = %s AND fecha_scraping >= CURRENT_DATE
                AND categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria
            """, (user_id,))
            cats_hoy = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Contar noticias por categoría AYER
            cursor.execute("""
                SELECT categoria, COUNT(*) FROM noticias 
                WHERE user_id = %s 
                AND fecha_scraping >= CURRENT_DATE - INTERVAL '1 day'
                AND fecha_scraping < CURRENT_DATE
                AND categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria
            """, (user_id,))
            cats_ayer = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Calcular Momentum y Proyección
            datos_radar = []
            max_momentum = -1.0
            categoria_dominante = "General"
            
            # Unir todas las categorías encontradas
            todas_categorias = set(cats_hoy.keys()) | set(cats_ayer.keys())
            
            if not todas_categorias:
                # Fallback si no hay datos
                categoria_dominante = "Sin datos suficientes"
                datos_radar = []
            else:
                for cat in todas_categorias:
                    vol_hoy = cats_hoy.get(cat, 0)
                    vol_ayer = cats_ayer.get(cat, 0)
                    
                    # Momentum: Crecimiento relativo
                    if vol_ayer > 0:
                        crecimiento = ((vol_hoy - vol_ayer) / vol_ayer)
                    else:
                        # Si ayer fue 0 y hoy hay noticias, es un crecimiento infinito/alto
                        crecimiento = 1.0 if vol_hoy > 0 else 0.0
                    
                    # Proyección simple para mañana (con factor de inercia 0.5)
                    proyeccion = int(vol_hoy * (1 + (crecimiento * 0.5)))
                    
                    datos_radar.append({
                        "subject": cat,
                        "hoy": vol_hoy,
                        "proyeccion": proyeccion,
                        "fullMark": max(vol_hoy, proyeccion) * 1.2 # Para escala del gráfico
                    })
                    
                    # Determinar dominante (priorizando volumen significativo > 2 noticias)
                    if vol_hoy > 2 and crecimiento > max_momentum:
                        max_momentum = crecimiento
                        categoria_dominante = cat
                
                # Si ninguna cumple el mínimo de volumen, tomar la de mayor volumen hoy
                if max_momentum == -1.0 and datos_radar:
                    datos_radar_sorted = sorted(datos_radar, key=lambda x: x['hoy'], reverse=True)
                    categoria_dominante = datos_radar_sorted[0]['subject']
                    max_momentum = 0.1 # Valor dummy positivo

                # Ordenar para el radar (Top 6 por volumen hoy para visualización limpia)
                datos_radar = sorted(datos_radar, key=lambda x: x['hoy'], reverse=True)[:6]

            tendencia_futura = {
                "tema": categoria_dominante,
                "probabilidad": min(80 + (max_momentum * 20), 99) if max_momentum > 0 else 50,
                "crecimiento": int(max_momentum * 100),
                "datos_radar": datos_radar
            }
                            
            # 2. Auto-Clasificador Inteligente
            # Buscar noticias sin categoría
            cursor.execute("""
                SELECT id, titulo, resumen FROM noticias 
                WHERE user_id = %s AND (categoria IS NULL OR categoria = '')
                LIMIT 3
            """, (user_id,))
            sin_categoria = cursor.fetchall()
            
            sugerencias = []
            if sin_categoria:
                # Obtener perfil de categorías del usuario (palabras clave por categoría)
                cursor.execute("""
                    SELECT categoria, titulo FROM noticias 
                    WHERE user_id = %s AND categoria IS NOT NULL AND categoria != ''
                    ORDER BY fecha_scraping DESC LIMIT 500
                """, (user_id,))
                historico = cursor.fetchall()
                
                perfil_categorias = {}
                for cat, tit in historico:
                    if cat not in perfil_categorias: perfil_categorias[cat] = []
                    perfil_categorias[cat].extend(tit.lower().split())
                
                for nid, tit, res in sin_categoria:
                    texto_analisis = (tit + " " + (res or "")).lower()
                    mejor_cat = "General"
                    max_score = 0
                    
                    for cat, palabras in perfil_categorias.items():
                        score = sum(1 for p in texto_analisis.split() if p in palabras and len(p) > 3)
                        if score > max_score:
                            max_score = score
                            mejor_cat = cat
                    
                    if max_score > 0:
                        sugerencias.append({
                            "id": nid,
                            "titulo": tit,
                            "categoria_sugerida": mejor_cat,
                            "confianza": min(40 + (max_score * 10), 98)
                        })

            # 3. Termómetro y Alertas de Sentimiento
            cursor.execute("""
                SELECT titulo, categoria FROM noticias 
                WHERE user_id = %s AND fecha_scraping >= NOW() - INTERVAL '24 hours'
            """, (user_id,))
            noticias_recientes = cursor.fetchall()
            
            total_sentimiento = 0
            conteo_sentimiento = 0
            sentimiento_por_cat = {}
            
            for tit, cat in noticias_recientes:
                score = self._analizar_sentimiento(tit)
                total_sentimiento += score
                conteo_sentimiento += 1
                
                if cat:
                    if cat not in sentimiento_por_cat: sentimiento_por_cat[cat] = []
                    sentimiento_por_cat[cat].append(score)
            
            # Promedio global (-1 a 1) -> Convertir a 0-100
            promedio_global = (total_sentimiento / conteo_sentimiento) if conteo_sentimiento > 0 else 0
            termometro = int((promedio_global + 1) * 50) # -1->0, 0->50, 1->100
            
            # Alertas
            alertas = []
            for cat, scores in sentimiento_por_cat.items():
                avg = sum(scores) / len(scores)
                if avg < -0.3: # Umbral de negatividad
                    alertas.append({
                        "tipo": "negativo",
                        "mensaje": f"Caída de confianza detectada en {cat}",
                        "nivel": "Alto" if avg < -0.6 else "Medio"
                    })
            
            return {
                "tendencia_futura": tendencia_futura,
                "sugerencias_clasificacion": sugerencias,
                "termometro_global": termometro,
                "alertas_sentimiento": alertas
            }
            
        except Exception as e:
            self._log(f"❌ Error en datos IA: {e}")
            import traceback
            self._log(traceback.format_exc())
            return {}
        finally:
            if should_close and cursor:
                cursor.close()
            if should_close and connection:
                connection.close()

    def obtener_dashboard_personalizado(self, user_id: int) -> Dict:
        """
        Obtiene métricas personalizadas para el dashboard del usuario.
        Incluye predicción de tendencias basada en frecuencia de palabras.
        """
        self._log(f"Iniciando dashboard personalizado para user_id={user_id}")
        connection = self.db.get_connection()
        if not connection:
            self._log("Error: No hay conexión DB en dashboard")
            return {}
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # 1. Métricas Generales (Hoy)
            cursor.execute("""
                SELECT COUNT(*) FROM noticias 
                WHERE user_id = %s AND fecha_scraping >= CURRENT_DATE
            """, (user_id,))
            noticias_hoy = cursor.fetchone()[0]
            
            # 2. Fuente Principal (con más noticias históricas)
            cursor.execute("""
                SELECT f.nombre, COUNT(n.id) as total
                FROM fuentes f
                JOIN noticias n ON f.id = n.fuente_id
                WHERE n.user_id = %s
                GROUP BY f.id, f.nombre
                ORDER BY total DESC
                LIMIT 1
            """, (user_id,))
            fuente_top = cursor.fetchone()
            
            # 3. Análisis de Palabras (Para Nube)
            cursor.execute("""
                SELECT titulo FROM noticias 
                WHERE user_id = %s 
                ORDER BY fecha_scraping DESC 
                LIMIT 100
            """, (user_id,))
            titulos = [row[0] for row in cursor.fetchall()]
            
            palabras_ignorar = {'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'de', 'del', 'a', 'en', 'que', 'por', 'para', 'con', 'se', 'su', 'sus', 'al', 'lo', 'como', 'mas', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'todo', 'esta', 'ser', 'son', 'dos', 'fue', 'era', 'muy', 'años', 'hasta', 'desde', 'mi', 'porque', 'qué', 'solo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'te', 'vida', 'otro', 'después', 'te', 'otro', 'donde', 'quien', 'ver', 'lugar', 'gran', 'pequeño', 'nuevo', 'antiguo', 'alto', 'bajo', 'bueno', 'malo', 'mayor', 'menor', 'mejor', 'peor', 'primer', 'ultimo', 'propio', 'ajeno', 'cierto', 'falso', 'puro', 'impuro', 'bello', 'feo', 'rico', 'pobre', 'alegre', 'triste', 'feliz', 'infeliz', 'sano', 'enfermo', 'fuerte', 'debil', 'libre', 'preso', 'vivo', 'muerto', 'dulce', 'amargo', 'caliente', 'frio', 'claro', 'oscuro', 'facil', 'dificil', 'duro', 'blando', 'lleno', 'vacio', 'limpio', 'sucio', 'seco', 'mojado', 'rapido', 'lento', 'cerca', 'lejos', 'arriba', 'abajo', 'delante', 'detras', 'dentro', 'fuera', 'izquierda', 'derecha', 'norte', 'sur', 'este', 'oeste', 'blanco', 'negro', 'rojo', 'azul', 'amarillo', 'verde', 'gris', 'marron', 'naranja', 'violeta', 'rosa', 'morado', 'celeste', 'turquesa', 'beige', 'crema', 'lila', 'fucsia', 'guinda', 'guinda', 'noticia', 'noticias', 'foto', 'video', 'audio', 'imagen'}
            
            frecuencia = {}
            for titulo in titulos:
                palabras = titulo.lower().replace(',', '').replace('.', '').replace(':', '').split()
                for palabra in palabras:
                    if len(palabra) > 3 and palabra not in palabras_ignorar:
                        frecuencia[palabra] = frecuencia.get(palabra, 0) + 1
            
            palabras_ordenadas = sorted(frecuencia.items(), key=lambda x: x[1], reverse=True)
            nube_palabras = [{"text": p, "value": c * 10} for p, c in palabras_ordenadas[:20]]
            
            # 4. Volumen por hora
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM fecha_scraping) as hora,
                    COUNT(*) as cantidad
                FROM noticias
                WHERE user_id = %s AND fecha_scraping >= NOW() - INTERVAL '24 hours'
                GROUP BY hora
                ORDER BY hora
            """, (user_id,))
            volumen_horas = [{"hora": f"{int(row[0]):02d}:00", "cantidad": row[1]} for row in cursor.fetchall()]
            
            # ✅ OBTENER DATOS DE IA (Pasando el cursor existente)
            datos_ia = self.obtener_datos_ia(user_id, cursor=cursor)
            
            self._log("Dashboard generado exitosamente")
            return {
                "resumen": {
                    "noticias_hoy": noticias_hoy,
                    "fuente_principal": {
                        "nombre": fuente_top[0] if fuente_top else "N/A",
                        "porcentaje": 0
                    },
                    "sentimiento": { 
                        "estado": "Positivo" if datos_ia.get('termometro_global', 50) > 60 else "Negativo" if datos_ia.get('termometro_global', 50) < 40 else "Neutro",
                        "emoji": "😃" if datos_ia.get('termometro_global', 50) > 60 else "😠" if datos_ia.get('termometro_global', 50) < 40 else "😐",
                        "valor": datos_ia.get('termometro_global', 50)
                    }
                },
                "prediccion": datos_ia.get('tendencia_futura', {}),
                "ia_insights": {
                    "sugerencias": datos_ia.get('sugerencias_clasificacion', []),
                    "alertas": datos_ia.get('alertas_sentimiento', []),
                    "termometro": datos_ia.get('termometro_global', 50)
                },
                "nube_palabras": nube_palabras,
                "volumen_horas": volumen_horas
            }
            
        except Exception as e:
            self._log(f"❌ Error dashboard personalizado: {e}")
            import traceback
            self._log(traceback.format_exc())
            return {}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
