import time
import os
import sys
import random
import signal
import datetime
import logging
from logging.handlers import RotatingFileHandler

class BotScheduler:
    """
    Clase para manejar la programación y ejecución continua del bot.
    """
    def __init__(self, callback_function, quota_manager, 
                 log_file='bot_scheduler.log',
                 error_log_file='bot_errors.log'):
        # Configurar el logger para operaciones normales
        self.logger = self._setup_logger('bot_scheduler', log_file)
        
        # Configurar logger separado para errores
        self.error_logger = self._setup_logger('bot_errors', error_log_file, 
                                              level=logging.ERROR)
        
        self.callback = callback_function
        self.quota_manager = quota_manager
        self.running = False
        self.next_run_time = None
        
        # Registrar señales para manejo limpio de parada
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _setup_logger(self, name, log_file, level=logging.INFO):
        """Configura un logger con rotación de archivos"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Evitar duplicados de handler
        if not logger.handlers:
            # Crear handler para archivo con rotación (5 archivos de 5MB)
            handler = RotatingFileHandler(
                log_file, maxBytes=5*1024*1024, backupCount=5)
            
            # Formato con timestamp, nivel y mensaje
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            
            # Añadir handler al logger
            logger.addHandler(handler)
            
            # También mostrar en consola
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)
        
        return logger

    def _handle_shutdown(self, signum, frame):
        """Maneja el apagado limpio del bot al recibir señales"""
        self.logger.info("Recibida señal de apagado. Deteniendo el bot...")
        self.running = False
        time.sleep(1)
        self.logger.info("Bot detenido correctamente")
        sys.exit(0)

    def _format_time_delta(self, minutes):
        """Formatea un número de minutos en un formato legible"""
        if minutes < 60:
            return f"{minutes} minutos"
        
        hours, mins = divmod(minutes, 60)
        if hours < 24:
            return f"{hours} horas, {mins} minutos"
        
        days, hours = divmod(hours, 24)
        return f"{days} días, {hours} horas, {mins} minutos"

    def run_forever(self, initial_delay=0, max_daily_uploads=None):
        """
        Ejecuta el bot en bucle infinito con la frecuencia óptima.
        
        Args:
            initial_delay: Minutos a esperar antes de la primera ejecución
            max_daily_uploads: Número máximo de subidas por día
        """
        self.running = True
        self.logger.info("Iniciando programador del bot en modo continuo")
        
        # Esperar el retraso inicial si se especifica
        if initial_delay > 0:
            delay_str = self._format_time_delta(initial_delay)
            self.logger.info(f"Esperando retraso inicial de {delay_str}")
            self.next_run_time = datetime.datetime.now() + datetime.timedelta(minutes=initial_delay)
            time.sleep(initial_delay * 60)
        
        # Bucle principal
        failures = 0
        while self.running:
            try:
                # Ejecutar el callback principal
                self.logger.info("Ejecutando ciclo del bot...")
                
                # Registrar la hora de inicio
                start_time = time.time()
                
                # Ejecutar el callback (puede ser el bot completo)
                success = self.callback()
                
                # Registrar duración de la ejecución
                duration = (time.time() - start_time) / 60  # en minutos
                self.logger.info(f"Ciclo completado en {duration:.2f} minutos")
                
                # Reiniciar contador de fallos si éxito
                if success:
                    failures = 0
                else:
                    failures += 1
                    self.error_logger.error(f"Fallo en la ejecución del bot. Intentos fallidos consecutivos: {failures}")
                
                # Si acumulamos muchos fallos, esperar más tiempo
                if failures >= 3:
                    backoff_minutes = min(60, 5 * failures)  # Máximo 1 hora
                    self.logger.warning(f"Demasiados fallos consecutivos. Esperando {backoff_minutes} minutos adicionales")
                    time.sleep(backoff_minutes * 60)
                    
                # Calcular tiempo óptimo para la próxima ejecución
                next_interval = self.quota_manager.calculate_optimal_frequency(max_daily_uploads)
                
                # Añadir un poco de aleatoriedad para que parezca más natural
                jitter = random.randint(-5, 5)
                next_interval = max(15, next_interval + jitter)  # Mínimo 15 minutos
                
                wait_str = self._format_time_delta(next_interval)
                self.next_run_time = datetime.datetime.now() + datetime.timedelta(minutes=next_interval)
                
                self.logger.info(f"Próxima ejecución en {wait_str} ({self.next_run_time.strftime('%Y-%m-%d %H:%M:%S')})")
                
                # Esperar hasta la próxima ejecución
                time.sleep(next_interval * 60)
                
            except KeyboardInterrupt:
                self.logger.info("Interrupción de teclado detectada. Deteniendo el bot...")
                self.running = False
                break
            except Exception as e:
                # Capturar cualquier excepción para evitar que el bot se detenga
                self.error_logger.exception(f"Error inesperado: {str(e)}")
                failures += 1
                
                # Backoff exponencial para errores
                backoff_minutes = min(60, 2 ** failures)  # Máximo 1 hora
                self.logger.error(f"Esperando {backoff_minutes} minutos antes del próximo intento")
                time.sleep(backoff_minutes * 60)
        
        self.logger.info("Bot detenido")

    def get_status(self):
        """Obtiene el estado actual del programador"""
        if not self.running:
            return "Detenido"
        
        if self.next_run_time:
            now = datetime.datetime.now()
            if self.next_run_time > now:
                minutes_remaining = (self.next_run_time - now).total_seconds() / 60
                return f"En espera, próxima ejecución en {self._format_time_delta(int(minutes_remaining))}"
            else:
                return "Ejecutando"
        
        return "En ejecución (horario no definido)"
