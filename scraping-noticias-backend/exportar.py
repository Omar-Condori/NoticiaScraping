import csv
import json
from io import StringIO
from typing import List, Dict

class Exportador:
    def __init__(self):
        pass
    
    def exportar_csv(self, noticias: List[Dict]) -> str:
        """Exporta noticias a formato CSV optimizado para ETL
        
        Incluye todos los campos relevantes en columnas separadas para
        facilitar procesos de extracción, transformación y carga de datos.
        """
        output = StringIO()
        
        if not noticias:
            return ""
        
        # ✅ COLUMNAS COMPLETAS PARA ETL (en orden lógico)
        columnas = [
            # Identificadores
            'id',
            'fuente_id',
            
            # Contenido principal
            'titulo',
            'resumen',
            'url',
            
            # Clasificación
            'categoria',
            'pais',
            
            # Información de fuente
            'fuente',
            
            # Recursos multimedia
            'imagen_url',
            
            # Metadatos temporales
            'fecha_publicacion',
            'fecha_scraping',
            
            # Otros campos
            'autor',
            'tags'
        ]
        
        writer = csv.DictWriter(
            output, 
            fieldnames=columnas, 
            extrasaction='ignore',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
        writer.writeheader()
        
        for noticia in noticias:
            # Asegurar que noticia es un diccionario
            if not isinstance(noticia, dict):
                noticia = dict(noticia)
            
            # Preparar fila con valores limpios
            fila = {}
            for col in columnas:
                valor = noticia.get(col, '')
                
                # Limpiar valores para CSV
                if valor is None:
                    fila[col] = ''
                elif isinstance(valor, (list, dict)):
                    # Convertir listas/dicts a string JSON
                    fila[col] = json.dumps(valor, ensure_ascii=False)
                else:
                    fila[col] = str(valor).strip()
            
            writer.writerow(fila)
        
        return output.getvalue()
    
    def exportar_json(self, noticias: List[Dict]) -> str:
        """Exporta noticias a formato JSON"""
        return json.dumps(noticias, indent=2, ensure_ascii=False)
    
    def exportar_txt(self, noticias: List[Dict]) -> str:
        """Exporta noticias a formato TXT legible"""
        output = []
        
        for i, noticia in enumerate(noticias, 1):
            output.append(f"{'='*80}")
            output.append(f"NOTICIA #{i}")
            output.append(f"{'='*80}")
            output.append(f"Título: {noticia.get('titulo', 'Sin título')}")
            output.append(f"Fuente: {noticia.get('fuente', 'Desconocida')}")
            output.append(f"URL: {noticia.get('url', 'N/A')}")
            output.append(f"Fecha: {noticia.get('fecha_scraping', 'N/A')}")
            output.append(f"\nResumen:\n{noticia.get('resumen', 'Sin resumen')}")
            output.append(f"\n")
        
        return '\n'.join(output)