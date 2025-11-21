import google.generativeai as genai
import os
from typing import Dict, List
from database import Database

class ChatBot:
    def __init__(self, db: Database):
        self.db = db
        # Configurar API Key desde variable de entorno o hardcoded (por ahora hardcoded para demo, idealmente ENV)
        # IMPORTANTE: El usuario debe configurar su API KEY aquí o en variables de entorno
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️ ADVERTENCIA: GEMINI_API_KEY no encontrada en variables de entorno.")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def generar_respuesta(self, user_id: int, pregunta: str) -> Dict:
        """
        Genera una respuesta usando Gemini basada en las noticias del usuario.
        """
        if not os.getenv('GEMINI_API_KEY'):
             return {
                "respuesta": "Error de configuración: API Key de Gemini no encontrada. Por favor contacta al administrador.",
                "fuentes": []
            }

        connection = self.db.get_connection()
        if not connection:
            return {"respuesta": "Error de conexión a la base de datos.", "fuentes": []}
        
        cursor = connection.cursor()
        try:
            # 1. Obtener contexto (últimas 20 noticias relevantes)
            # Idealmente haríamos búsqueda semántica, pero por ahora usamos las más recientes
            cursor.execute("""
                SELECT titulo, resumen, categoria, fecha_scraping 
                FROM noticias 
                WHERE user_id = %s 
                ORDER BY fecha_scraping DESC 
                LIMIT 20
            """, (user_id,))
            
            noticias = cursor.fetchall()
            
            if not noticias:
                return {
                    "respuesta": "No he encontrado noticias guardadas en tu cuenta para responder a esta pregunta. ¡Prueba scrapeando algunas noticias primero!",
                    "fuentes": []
                }
            
            # 2. Construir Prompt
            contexto_texto = ""
            for titulo, resumen, cat, fecha in noticias:
                contexto_texto += f"- [{fecha}] ({cat}) {titulo}: {resumen}\n"
            
            prompt = f"""
            Eres un 'Asistente de Noticias' inteligente y útil.
            Tu objetivo es responder a la pregunta del usuario basándote EXCLUSIVAMENTE en la siguiente lista de noticias que el usuario ha recolectado.
            
            Si la respuesta no se encuentra en las noticias proporcionadas, di amablemente que no tienes información sobre ese tema en las noticias guardadas.
            No inventes información. Cita las noticias relevantes si es posible.
            
            INFORMACIÓN DEL USUARIO (NOTICIAS):
            {contexto_texto}
            
            PREGUNTA DEL USUARIO:
            {pregunta}
            
            RESPUESTA:
            """
            
            # 3. Llamar a Gemini
            response = self.model.generate_content(prompt)
            
            return {
                "respuesta": response.text,
                "fuentes": [n[0] for n in noticias[:3]] # Retornar títulos de las 3 más recientes como referencia
            }
            
        except Exception as e:
            print(f"❌ Error en ChatBot: {e}")
            return {
                "respuesta": "Lo siento, ocurrió un error al procesar tu pregunta con la IA.",
                "error": str(e)
            }
        finally:
            cursor.close()
            connection.close()
