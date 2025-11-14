import csv
import json
from io import StringIO
from typing import List, Dict

class Exportador:
    def __init__(self):
        pass
    
    def exportar_csv(self, noticias: List[Dict]) -> str:
        """Exporta noticias a formato CSV"""
        output = StringIO()
        
        if not noticias:
            return ""
        
        # Definir columnas
        columnas = ['id', 'titulo', 'url', 'resumen', 'fuente', 'fecha_scraping']
        
        writer = csv.DictWriter(output, fieldnames=columnas, extrasaction='ignore')
        writer.writeheader()
        
        for noticia in noticias:
            writer.writerow(noticia)
        
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