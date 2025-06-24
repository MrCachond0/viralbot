import os
import sys
import json
import webbrowser
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
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

def main():
    print_header("MÉTODO ALTERNATIVO PARA OBTENER TOKENS DE YOUTUBE")
    
    # Verificar que existe client_secret.json
    if not os.path.exists("client_secret.json"):
        print_error("No se encontró el archivo client_secret.json")
        print("Debes descargar este archivo desde la consola de Google Cloud.")
        print("1. Ve a https://console.cloud.google.com/")
        print("2. Selecciona tu proyecto")
        print("3. Ve a 'APIs y servicios' > 'Credenciales'")
        print("4. Descarga el JSON de tu cliente OAuth")
        print("5. Guárdalo como 'client_secret.json' en este directorio")
        sys.exit(1)
    
    # Intentar método alternativo usando InstalledAppFlow con redirect_uri manual
    print_step(1, "Configurando autenticación alternativa...")
    
    try:
        # Este método utiliza la redirección a la consola en lugar de un servidor local
        # Usamos un scope menos restrictivo para mayor probabilidad de éxito
        SCOPES = [
            "https://www.googleapis.com/auth/youtube",  # Scope completo, menos restrictivo
            "https://www.googleapis.com/auth/youtube.upload"
        ]
        
        # Cargar las credenciales desde client_secret.json
        with open("client_secret.json", "r") as f:
            client_config = json.load(f)
        
        # Crear una copia del client_secret para modificarla
        client_config_copy = json.loads(json.dumps(client_config))
        
        # Modificar la configuración para usar redirect_uri OOB (fuera de navegador)
        if "installed" in client_config_copy:
            client_config_copy["installed"]["redirect_uris"] = ["urn:ietf:wg:oauth:2.0:oob"]
        elif "web" in client_config_copy:
            # Crear una nueva estructura 'installed' basada en 'web'
            client_config_copy["installed"] = {
                "client_id": client_config_copy["web"]["client_id"],
                "project_id": client_config_copy["web"]["project_id"],
                "auth_uri": client_config_copy["web"]["auth_uri"],
                "token_uri": client_config_copy["web"]["token_uri"],
                "auth_provider_x509_cert_url": client_config_copy["web"]["auth_provider_x509_cert_url"],
                "client_secret": client_config_copy["web"]["client_secret"],
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
            }
            # Eliminar la sección 'web'
            del client_config_copy["web"]
        
        # Instrucciones claras para el usuario
        print_warning("Se abrirá una ventana en tu navegador para que autorices la aplicación.")
        print_warning("IMPORTANTE - Sigue estos pasos exactamente:")
        print("1. Inicia sesión con tu cuenta de Google (la misma que usas para YouTube)")
        print("2. Si ves una advertencia 'Google no ha verificado esta aplicación':")
        print("   - Haz clic en 'Avanzado' (abajo a la izquierda)")
        print("   - Luego haz clic en 'Ir a [Nombre de tu proyecto] (no seguro)'")
        print("3. En la pantalla de permisos, haz clic en 'Permitir'")
        print("4. Verás un código de autorización. COPIA este código.")
        print("5. Vuelve a esta ventana y PEGA el código cuando se te solicite.")
        
        # Esperar a que el usuario lea las instrucciones
        input("\nPresiona Enter cuando estés listo para continuar...")
        
        # Crear el flujo de autenticación
        flow = InstalledAppFlow.from_client_config(
            client_config_copy,
            SCOPES,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        
        # Obtener la URL de autorización
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )
        
        # Abrir el navegador con la URL de autorización
        print_step(2, "Abriendo navegador para autorización...")
        print(f"Si el navegador no se abre automáticamente, visita esta URL: {auth_url}")
        webbrowser.open(auth_url)
        
        # Solicitar el código de autorización al usuario
        print_step(3, "Ingresando código de autorización...")
        code = input("Ingresa el código de autorización que recibiste: ").strip()
        
        if not code:
            print_error("No se ingresó ningún código. Operación cancelada.")
            sys.exit(1)
        
        # Intercambiar el código por credenciales
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Guardar las credenciales en ambos formatos
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
        import pickle
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
        
        print_success("Credenciales guardadas en token.json y token.pickle")
        
        # Actualizar el archivo .env
        print_step(4, "Actualizando archivo .env...")
        
        # Cargar el archivo .env
        load_dotenv()
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Obtener el ID del canal
        print_step(5, "Obteniendo ID del canal de YouTube...")
        try:
            youtube = build("youtube", "v3", credentials=creds)
            response = youtube.channels().list(part="id,snippet", mine=True).execute()
            
            if not response.get("items"):
                print_error("No se encontró ningún canal asociado a esta cuenta de Google")
                channel_id = ""
                channel_name = ""
            else:
                channel_id = response["items"][0]["id"]
                channel_name = response["items"][0]["snippet"]["title"]
                print_success(f"CHANNEL ID: {channel_id}")
                print_success(f"CHANNEL NAME: {channel_name}")
        except Exception as e:
            print_error(f"Error al obtener información del canal: {str(e)}")
            print("Continuando sin ID de canal...")
            channel_id = ""
        
        # Actualizar variables en .env
        env_vars = {
            "YOUTUBE_ACCESS_TOKEN": creds.token,
            "YOUTUBE_REFRESH_TOKEN": creds.refresh_token,
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
        
        print_success("Tokens y ID del canal guardados correctamente en .env")
        
        # Mostrar resultados
        print_header("PROCESO COMPLETADO")
        print_success(f"ACCESS TOKEN: {creds.token[:15]}...")
        print_success(f"REFRESH TOKEN: {creds.refresh_token[:15]}...")
        if channel_id:
            print_success(f"CHANNEL ID: {channel_id}")
        
        print("\nAhora puedes ejecutar el bot con:")
        print("python bot.py")
        
        print("\nSi sigues teniendo problemas, prueba ejecutando el bot sin subir a YouTube:")
        print("python bot.py --no-upload")
        
    except HttpError as e:
        print_error(f"Error de API: {e.reason}")
        print("Asegúrate de que la API de YouTube esté habilitada en tu proyecto de Google Cloud")
        print("\nPuedes probar el bot sin subir a YouTube con:")
        print("python bot.py --no-upload")
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPuedes probar el bot sin subir a YouTube con:")
        print("python bot.py --no-upload")

if __name__ == "__main__":
    main()
