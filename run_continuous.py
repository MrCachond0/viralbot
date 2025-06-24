import os
import sys
import argparse
from dotenv import load_dotenv
from bot import main_bot_process
from quota_manager import QuotaManager
from bot_scheduler import BotScheduler

def run_continuous_bot():
    """
    Ejecuta el bot en modo continuo, gestionando la frecuencia y respetando
    las cuotas de la API de YouTube.
    """
    print('=' * 60)
    print('REDDIT SHORTS BOT - MODO CONTINUO 24/7')
    print('=' * 60)
    
    # Procesar argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='Bot para generar videos de Reddit y subirlos a YouTube en modo continuo')
    parser.add_argument('--max-daily', type=int, default=5,
                       help='Número máximo de videos a subir por día (default: 5)')
    parser.add_argument('--initial-delay', type=int, default=0,
                       help='Tiempo de espera inicial en minutos antes de la primera ejecución (default: 0)')
    parser.add_argument('--no-upload', action='store_true',
                       help='Solo genera videos, sin subirlos a YouTube')
    args = parser.parse_args()
    
    # Verificar si existen credenciales
    load_dotenv()
    if not os.getenv('CLIENT_ID') or not os.getenv('CLIENT_SECRET'):
        print("ERROR: Faltan credenciales de Reddit en el archivo .env")
        print("Por favor, configura CLIENT_ID y CLIENT_SECRET en el archivo .env")
        sys.exit(1)
    
    if not args.no_upload and not (os.path.exists('client_secret.json') or 
                                 (os.getenv('YOUTUBE_REFRESH_TOKEN') and os.getenv('YOUTUBE_CLIENT_ID'))):
        print("ERROR: Faltan credenciales de YouTube")
        print("Por favor, ejecuta primero get_youtube_tokens.py o configura las variables de YouTube en .env")
        sys.exit(1)
    
    # Crear un administrador de cuotas
    quota_manager = QuotaManager()
    
    # Función de callback que ejecutará el bot
    def run_bot_cycle():
        try:
            print("\n\nIniciando nuevo ciclo de bot...")
            result = main_bot_process(args.no_upload)
            return result
        except Exception as e:
            print(f"Error en ciclo del bot: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    # Crear el programador del bot
    scheduler = BotScheduler(run_bot_cycle, quota_manager)
    
    # Mostrar configuración
    print(f"\nConfiguración del bot:")
    print(f"- Modo subida: {'DESACTIVADO (--no-upload)' if args.no_upload else 'ACTIVADO'}")
    print(f"- Máximo diario: {args.max_daily} videos")
    print(f"- Retraso inicial: {args.initial_delay} minutos")
    
    # Verificar cuota disponible
    remaining_quota = quota_manager.get_remaining_quota()
    print(f"\nCuota API YouTube disponible hoy: {remaining_quota}/{QuotaManager.DAILY_QUOTA} unidades")
    print(f"Videos posibles hoy: {remaining_quota // QuotaManager.UPLOAD_COST}")
    
    try:
        print("\nIniciando bot en modo continuo. Presiona Ctrl+C para detener.")
        print("Los logs se guardarán en bot_scheduler.log y bot_errors.log")
        
        # Iniciar el bucle continuo
        scheduler.run_forever(
            initial_delay=args.initial_delay, 
            max_daily_uploads=args.max_daily
        )
    except KeyboardInterrupt:
        print("\nBot detenido por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_continuous_bot()
