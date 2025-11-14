from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json

class ScraperScheduler:
    def __init__(self, scraper):
        """Inicializa el programador de tareas"""
        self.scraper = scraper
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.tareas_activas = {}
        
    def agregar_tarea(self, nombre: str, intervalo_minutos: int, fuente_id=None, limite=5):
        """
        Agrega una tarea programada de scraping
        
        Args:
            nombre: Identificador único de la tarea
            intervalo_minutos: Cada cuántos minutos ejecutar
            fuente_id: ID de fuente específica (None para todas)
            limite: Noticias por fuente
        """
        if nombre in self.tareas_activas:
            return {'error': 'Ya existe una tarea con ese nombre'}
        
        def job():
            print(f"⏰ Ejecutando tarea programada: {nombre}")
            try:
                if fuente_id:
                    fuente = self.scraper.obtener_fuente(fuente_id)
                    if fuente:
                        self.scraper.scrape_fuente(fuente, limite, guardar=True)
                else:
                    self.scraper.scrape_todas_fuentes(limite, guardar=True)
                print(f"✅ Tarea {nombre} completada")
            except Exception as e:
                print(f"❌ Error en tarea {nombre}: {e}")
        
        # Agregar tarea al scheduler
        job_instance = self.scheduler.add_job(
            job,
            'interval',
            minutes=intervalo_minutos,
            id=nombre,
            next_run_time=datetime.now()  # Ejecutar inmediatamente la primera vez
        )
        
        self.tareas_activas[nombre] = {
            'nombre': nombre,
            'intervalo_minutos': intervalo_minutos,
            'fuente_id': fuente_id,
            'limite': limite,
            'activa': True,
            'proxima_ejecucion': str(job_instance.next_run_time)
        }
        
        return self.tareas_activas[nombre]
    
    def eliminar_tarea(self, nombre: str):
        """Elimina una tarea programada"""
        if nombre not in self.tareas_activas:
            return False
        
        try:
            self.scheduler.remove_job(nombre)
            del self.tareas_activas[nombre]
            print(f"🗑️  Tarea {nombre} eliminada")
            return True
        except Exception as e:
            print(f"❌ Error eliminando tarea: {e}")
            return False
    
    def listar_tareas(self):
        """Lista todas las tareas programadas"""
        tareas = []
        for nombre, info in self.tareas_activas.items():
            job = self.scheduler.get_job(nombre)
            if job:
                info['proxima_ejecucion'] = str(job.next_run_time)
            tareas.append(info)
        return tareas
    
    def obtener_tarea(self, nombre: str):
        """Obtiene información de una tarea específica"""
        if nombre not in self.tareas_activas:
            return None
        
        info = self.tareas_activas[nombre].copy()
        job = self.scheduler.get_job(nombre)
        if job:
            info['proxima_ejecucion'] = str(job.next_run_time)
        return info
    
    def pausar_tarea(self, nombre: str):
        """Pausa una tarea"""
        if nombre not in self.tareas_activas:
            return False
        
        try:
            self.scheduler.pause_job(nombre)
            self.tareas_activas[nombre]['activa'] = False
            return True
        except Exception as e:
            print(f"❌ Error pausando tarea: {e}")
            return False
    
    def reanudar_tarea(self, nombre: str):
        """Reanuda una tarea pausada"""
        if nombre not in self.tareas_activas:
            return False
        
        try:
            self.scheduler.resume_job(nombre)
            self.tareas_activas[nombre]['activa'] = True
            return True
        except Exception as e:
            print(f"❌ Error reanudando tarea: {e}")
            return False
    
    def detener_scheduler(self):
        """Detiene el scheduler (llamar al cerrar la app)"""
        self.scheduler.shutdown()