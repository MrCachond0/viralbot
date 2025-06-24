import json
import os
from datetime import datetime, timedelta
import random

class QuotaManager:
    """
    Clase para gestionar las cuotas de la API de YouTube y optimizar la frecuencia
    de publicación para maximizar el potencial viral sin exceder límites.
    """
    # Cuota diaria de la API de YouTube (10,000 unidades)
    # Cada subida de video consume aproximadamente 1,600 unidades
    DAILY_QUOTA = 10000
    UPLOAD_COST = 1600
    
    def __init__(self, quota_file='quota_stats.json'):
        self.quota_file = quota_file
        self.stats = self._load_stats()
        self._clean_old_stats()

    def _load_stats(self):
        """Carga las estadísticas de uso de cuota desde el archivo"""
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error al leer el archivo {self.quota_file}, creando nuevas estadísticas")
                return {"uploads": [], "daily_usage": {}}
        else:
            return {"uploads": [], "daily_usage": {}}

    def _save_stats(self):
        """Guarda las estadísticas de uso de cuota en el archivo"""
        with open(self.quota_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def _clean_old_stats(self):
        """Elimina estadísticas de más de 30 días para mantener el archivo limpio"""
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Limpiar uploads antiguos
        self.stats["uploads"] = [
            upload for upload in self.stats["uploads"] 
            if upload["date"] >= thirty_days_ago
        ]
        
        # Limpiar estadísticas diarias antiguas
        self.stats["daily_usage"] = {
            date: usage for date, usage in self.stats["daily_usage"].items() 
            if date >= thirty_days_ago
        }
        
        self._save_stats()

    def register_upload(self, video_id, quota_used=UPLOAD_COST):
        """Registra una nueva subida de video y su uso de cuota"""
        today = datetime.now().date().isoformat()
        
        # Registrar la subida
        upload_data = {
            "video_id": video_id,
            "date": datetime.now().isoformat(),
            "quota_used": quota_used
        }
        self.stats["uploads"].append(upload_data)
        
        # Actualizar el uso diario
        if today not in self.stats["daily_usage"]:
            self.stats["daily_usage"][today] = 0
        self.stats["daily_usage"][today] += quota_used
        
        self._save_stats()

    def get_today_usage(self):
        """Obtiene el uso de cuota del día actual"""
        today = datetime.now().date().isoformat()
        return self.stats["daily_usage"].get(today, 0)

    def get_remaining_quota(self):
        """Obtiene la cuota restante para hoy"""
        return self.DAILY_QUOTA - self.get_today_usage()

    def can_upload(self):
        """Determina si es posible realizar una nueva subida hoy"""
        return self.get_remaining_quota() >= self.UPLOAD_COST

    def get_uploads_today(self):
        """Obtiene el número de subidas realizadas hoy"""
        today = datetime.now().date().isoformat()
        today_timestamp = datetime.fromisoformat(today).timestamp()
        
        count = 0
        for upload in self.stats["uploads"]:
            upload_date = datetime.fromisoformat(upload["date"]).timestamp()
            if upload_date >= today_timestamp:
                count += 1
        
        return count

    def calculate_optimal_frequency(self, max_daily_uploads=None):
        """
        Calcula la frecuencia óptima de publicación basada en la cuota disponible
        y el objetivo de maximizar el alcance viral.
        
        La estrategia busca:
        1. No exceder nunca la cuota diaria
        2. Distribuir videos a lo largo del día para captar diferentes audiencias
        3. Introducir aleatoriedad para evitar patrones predecibles
        
        Returns:
            int: Minutos a esperar hasta la próxima subida
        """
        # Si no se especifica, calcular máximo de subidas posibles por día
        if max_daily_uploads is None:
            max_daily_uploads = self.DAILY_QUOTA // self.UPLOAD_COST
        
        # Para evitar problemas, limitar a un máximo razonable (para 10,000 unidades ≈ 6 videos)
        max_daily_uploads = min(max_daily_uploads, 6)
        
        # Obtener el número de subidas realizadas hoy
        uploads_today = self.get_uploads_today()
        
        # Si ya hemos alcanzado el máximo, esperar hasta mañana
        if uploads_today >= max_daily_uploads or not self.can_upload():
            # Calcular tiempo hasta la medianoche
            now = datetime.now()
            tomorrow = datetime.combine(now.date() + timedelta(days=1), 
                                        datetime.min.time())
            # Añadir entre 5-30 minutos aleatorios para evitar exactamente medianoche
            random_minutes = random.randint(5, 30)
            wait_time = (tomorrow - now).total_seconds() / 60 + random_minutes
            return int(wait_time)
        
        # Estrategia: Distribuir las subidas restantes en el tiempo que queda del día
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), 
                                    datetime.min.time())
        minutes_left_today = (midnight - now).total_seconds() / 60
        
        # Subidas restantes posibles hoy
        uploads_left = min(max_daily_uploads - uploads_today, 
                           self.get_remaining_quota() // self.UPLOAD_COST)
        
        if uploads_left <= 0:
            # No deberíamos llegar aquí debido a la verificación anterior
            return int(minutes_left_today)
        
        # Distribuir el tiempo restante entre las subidas pendientes
        base_interval = minutes_left_today / (uploads_left + 1)  # +1 para evitar subir justo a medianoche
        
        # Añadir un factor aleatorio (±20%) para evitar patrones predecibles
        randomness = base_interval * 0.2
        next_interval = base_interval + random.uniform(-randomness, randomness)
        
        # Garantizar un mínimo de 15 minutos entre subidas
        return max(15, int(next_interval))
