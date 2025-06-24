import os
import sys
import json
import time
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Colores para la terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== {text} ==={Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_step(step_num, text):
    print(f"{Colors.BOLD}[{step_num}] {text}{Colors.END}")

def update_env_file(access_token, refresh_token, channel_id):
    """Actualiza el archivo .env con los tokens obtenidos"""
    try:
        env_path = ".env"
        
        # Leer el archivo actual
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = []

        # Actualizar o agregar las variables
        env_vars = {
            "YOUTUBE_ACCESS_TOKEN": access_token,
            "YOUTUBE_REFRESH_TOKEN": refresh_token,
            "YOUTUBE_CHANNEL_ID": channel_id
        }
        
        updated = {key: False for key in env_vars.keys()}
        
        # Actualizar líneas existentes
        for i, line in enumerate(lines):
            for key in env_vars:
                if line.strip().startswith(f"{key}="):
                    lines[i] = f"{key}={env_vars[key]}\n"
                    updated[key] = True
        
        # Agregar variables que no existen
        for key, value in env_vars.items():
            if not updated[key]:
                lines.append(f"{key}={value}\n")
        
        # Escribir el archivo actualizado
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        print_success(f"Archivo .env actualizado con los tokens y el ID del canal")
    except Exception as e:
        print_error(f"Error al actualizar el archivo .env: {str(e)}")
        print("Deberás actualizar manualmente las variables en el archivo .env")
        print(f"YOUTUBE_ACCESS_TOKEN={access_token}")
        print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
        print(f"YOUTUBE_CHANNEL_ID={channel_id}")

def verify_client_secret():
    """Verifica que el archivo client_secret.json existe y tiene el formato correcto"""
    if not os.path.exists("client_secret.json"):
        print_error("No se encontró el archivo client_secret.json")
        print("Debes descargar el archivo client_secret.json desde la consola de Google Cloud.")
        print("1. Ve a https://console.developers.google.com/")
        print("2. Selecciona tu proyecto")
        print("3. Ve a 'Credenciales'")
        print("4. Descarga el JSON de tu cliente OAuth")
        print("5. Guárdalo como 'client_secret.json' en este directorio")
        return False
        
    try:
        with open("client_secret.json", "r") as f:
            data = json.load(f)
        
        # Verificar si tiene la estructura correcta
        if "installed" not in data and "web" not in data:
            print_error("El archivo client_secret.json no tiene el formato correcto")
            return False
            
        return True
    except json.JSONDecodeError:
        print_error("El archivo client_secret.json no es un JSON válido")
        return False
    except Exception as e:
        print_error(f"Error al leer client_secret.json: {str(e)}")
        return False

def get_tokens():
    """Obtiene los tokens de acceso y refresco usando OAuth"""
    print_header("OBTENCIÓN DE TOKENS DE YOUTUBE")
    
    # Verificar client_secret.json
    print_step(1, "Verificando el archivo client_secret.json...")
    if not verify_client_secret():
        sys.exit(1)
    print_success("Archivo client_secret.json verificado correctamente")
    
    # Instrucciones importantes para el usuario
    print_header("INSTRUCCIONES IMPORTANTES")
    print("Para resolver el error 403: access_denied, asegúrate de seguir estos pasos:")
    print("1. Debes haber agregado tu cuenta como 'usuario de prueba' en la consola de Google Cloud")
    print("   (Ve a APIs y servicios > Pantalla de consentimiento > Usuarios de prueba)")
    print("2. Inicia sesión con la misma cuenta que agregaste como usuario de prueba")
    print("3. Cuando veas la advertencia 'Google no ha verificado esta aplicación':")
    print("   - Haz clic en 'Avanzado' o 'Configuración'")
    print("   - Luego haz clic en 'Ir a [Nombre de tu proyecto] (no seguro)'")
    print("4. En la pantalla de permisos, haz clic en 'Continuar' o 'Permitir'")
    print("\nPara más detalles, consulta el archivo 'solucion_error_oauth.md'")
    
    # Esperar a que el usuario lea las instrucciones
    input("\nPresiona Enter cuando estés listo para continuar...")
    
    # Configurar el flujo de OAuth
    print_step(2, "Iniciando el proceso de autorización...")
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        
        print_warning("Se abrirá una ventana en tu navegador para que autorices la aplicación.")
        print_warning("Asegúrate de iniciar sesión con la cuenta de Google que has agregado como usuario de prueba.")
        print_warning("IMPORTANTE: Cuando veas la advertencia 'Google no ha verificado esta aplicación':")
        print_warning("1. Haz clic en 'Avanzado' o 'Configuración'")
        print_warning("2. Luego haz clic en 'Ir a [Nombre de tu proyecto] (no seguro)'")
        print_warning("3. Asegúrate de ACEPTAR todos los permisos solicitados")
        
        # Esperar 5 segundos para que el usuario lea el mensaje
        time.sleep(5)
        
        creds = flow.run_local_server(port=0)
        
        # Guardar las credenciales en un archivo pickle
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
        
        print_success("Autorización completada correctamente")
        print_success(f"ACCESS TOKEN: {creds.token}")
        print_success(f"REFRESH TOKEN: {creds.refresh_token}")
        
        return creds
        
    except Exception as e:
        print_error(f"Error durante la autorización: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Asegúrate de que la API de YouTube esté habilitada en tu proyecto de Google Cloud")
        print("2. Verifica que las credenciales OAuth tengan los ámbitos correctos configurados")
        print("3. Asegúrate de que tu cuenta esté agregada como 'usuario de prueba'")
        print("4. Comprueba que tu proyecto de Google Cloud tenga habilitada la pantalla de consentimiento OAuth")
        print("5. En la pantalla de autorización, asegúrate de hacer clic en 'Avanzado' y luego en 'Ir a [Nombre de tu proyecto]'")
        print("6. Asegúrate de ACEPTAR todos los permisos solicitados")
        print("\nConsulta el archivo 'solucion_error_oauth.md' para instrucciones detalladas")
        print("\nPara obtener más ayuda, consulta: https://developers.google.com/youtube/v3/guides/auth/installed-apps")
        sys.exit(1)

def get_channel_id(creds):
    """Obtiene el ID del canal de YouTube usando las credenciales"""
    print_step(3, "Obteniendo ID del canal de YouTube...")
    
    try:
        youtube = build("youtube", "v3", credentials=creds)
        response = youtube.channels().list(part="id", mine=True).execute()
        
        if not response.get("items"):
            print_error("No se encontró ningún canal asociado a esta cuenta de Google")
            print("Asegúrate de haber iniciado sesión con una cuenta que tenga un canal de YouTube")
            return None
        
        channel_id = response["items"][0]["id"]
        print_success(f"CHANNEL ID: {channel_id}")
        return channel_id
        
    except HttpError as e:
        print_error(f"Error al obtener el ID del canal: {e.reason}")
        print("Asegúrate de que la API de YouTube esté habilitada en tu proyecto de Google Cloud")
        return None
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return None

def main():
    try:
        # Obtener tokens
        creds = get_tokens()
        
        # Obtener ID del canal
        channel_id = get_channel_id(creds)
        
        if channel_id:
            # Actualizar archivo .env
            update_env_file(creds.token, creds.refresh_token, channel_id)
            
            print_header("PROCESO COMPLETADO")
            print("Los tokens y el ID del canal se han obtenido correctamente y se han guardado en el archivo .env")
            print("\nAhora puedes ejecutar el bot.py para generar y subir videos a YouTube automáticamente.")
        else:
            print_error("No se pudo completar el proceso porque no se obtuvo el ID del canal")
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario.")
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()