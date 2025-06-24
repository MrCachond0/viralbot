import os
import sys
import json
import requests
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

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_step(step_num, text):
    print(f"{Colors.BOLD}[{step_num}] {text}{Colors.END}")

def check_client_secret_file():
    """Verifica el archivo client_secret.json"""
    print_step(1, "Verificando archivo client_secret.json...")
    
    if not os.path.exists("client_secret.json"):
        print_error("No se encontró el archivo client_secret.json")
        print("Debes descargar este archivo desde la consola de Google Cloud")
        return False
    
    try:
        with open("client_secret.json", "r") as f:
            data = json.load(f)
        
        # Verificar la estructura del archivo
        if "installed" in data:
            client_id = data["installed"].get("client_id", "")
            client_secret = data["installed"].get("client_secret", "")
            redirect_uris = data["installed"].get("redirect_uris", [])
            
            print_success("Archivo client_secret.json es válido (tipo: instalada)")
            print_info(f"Client ID: {client_id[:15]}...")
            print_info(f"Client Secret: {client_secret[:5]}...")
            
            if "http://localhost" in redirect_uris or "localhost" in str(redirect_uris):
                print_success("URIs de redirección incluyen localhost (correcto)")
            else:
                print_warning("URIs de redirección no incluyen localhost")
                print_info(f"URIs configurados: {redirect_uris}")
            
            return True
        elif "web" in data:
            print_warning("El archivo client_secret.json es para una aplicación web, no para una aplicación instalada")
            print("Esto podría causar problemas. Considera crear credenciales para una 'Aplicación de Escritorio'")
            return True
        else:
            print_error("Formato de client_secret.json no reconocido")
            return False
            
    except json.JSONDecodeError:
        print_error("El archivo client_secret.json no es un JSON válido")
        return False
    except Exception as e:
        print_error(f"Error al leer client_secret.json: {str(e)}")
        return False

def check_env_variables():
    """Verifica las variables de entorno relacionadas con YouTube"""
    print_step(2, "Verificando variables de entorno...")
    
    load_dotenv()
    
    variables = {
        "YOUTUBE_CLIENT_ID": os.getenv("YOUTUBE_CLIENT_ID"),
        "YOUTUBE_CLIENT_SECRET": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "YOUTUBE_ACCESS_TOKEN": os.getenv("YOUTUBE_ACCESS_TOKEN"),
        "YOUTUBE_REFRESH_TOKEN": os.getenv("YOUTUBE_REFRESH_TOKEN"),
        "YOUTUBE_CHANNEL_ID": os.getenv("YOUTUBE_CHANNEL_ID")
    }
    
    all_set = True
    for name, value in variables.items():
        if value:
            if name in ["YOUTUBE_CLIENT_SECRET", "YOUTUBE_ACCESS_TOKEN", "YOUTUBE_REFRESH_TOKEN"]:
                # Mostrar solo primeros caracteres para secretos
                display_value = f"{value[:5]}..." if value else "No configurado"
            else:
                display_value = value
            print_success(f"{name}: {display_value}")
        else:
            print_warning(f"{name}: No configurado")
            all_set = False
    
    return all_set

def check_youtube_api_access():
    """Intenta hacer una petición simple a la API de YouTube para verificar el acceso"""
    print_step(3, "Verificando acceso a la API de YouTube...")
    
    token = os.getenv("YOUTUBE_ACCESS_TOKEN")
    if not token:
        print_warning("No se puede verificar el acceso a la API porque no hay token de acceso configurado")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                channel_title = data["items"][0]["snippet"]["title"]
                print_success(f"Acceso correcto a la API de YouTube")
                print_info(f"Canal: {channel_title}")
                return True
            else:
                print_warning("Respuesta válida pero no se encontró información del canal")
                return False
        else:
            print_error(f"Error al acceder a la API: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            
            if response.status_code == 401:
                print_warning("El token de acceso ha expirado o es inválido")
                print("Ejecuta get_youtube_tokens.py para obtener un nuevo token")
            
            return False
            
    except Exception as e:
        print_error(f"Error al verificar el acceso a la API: {str(e)}")
        return False

def check_google_cloud_project():
    """Intenta obtener información del proyecto de Google Cloud"""
    print_step(4, "Verificando configuración del proyecto en Google Cloud...")
    
    try:
        with open("client_secret.json", "r") as f:
            data = json.load(f)
        
        project_id = None
        if "installed" in data and "project_id" in data["installed"]:
            project_id = data["installed"]["project_id"]
        elif "web" in data and "project_id" in data["web"]:
            project_id = data["web"]["project_id"]
        
        if project_id:
            print_info(f"Project ID: {project_id}")
            print_info("Asegúrate de que este proyecto tenga la API de YouTube habilitada")
            print_info("URL: https://console.cloud.google.com/apis/library/youtube.googleapis.com")
        else:
            print_warning("No se pudo determinar el ID del proyecto desde client_secret.json")
        
    except Exception as e:
        print_warning(f"No se pudo verificar la configuración del proyecto: {str(e)}")

def main():
    print_header("DIAGNÓSTICO DE CONFIGURACIÓN PARA YOUTUBE API")
    
    client_secret_ok = check_client_secret_file()
    env_vars_ok = check_env_variables()
    api_access_ok = check_youtube_api_access()
    check_google_cloud_project()
    
    print_header("RESULTADOS DEL DIAGNÓSTICO")
    
    if client_secret_ok:
        print_success("✓ Archivo client_secret.json: OK")
    else:
        print_error("✗ Archivo client_secret.json: Problemas detectados")
    
    if env_vars_ok:
        print_success("✓ Variables de entorno: OK")
    else:
        print_warning("⚠ Variables de entorno: Faltan algunas variables")
    
    if api_access_ok:
        print_success("✓ Acceso a la API de YouTube: OK")
    else:
        print_warning("⚠ Acceso a la API de YouTube: Problemas detectados")
    
    print("\nPASOSPARA SOLUCIONAR PROBLEMAS:")
    print("1. Asegúrate de que la API de YouTube esté habilitada en tu proyecto de Google Cloud")
    print("2. Verifica que las credenciales OAuth tengan los ámbitos correctos")
    print("3. Ejecuta get_youtube_tokens.py para regenerar los tokens")
    print("4. Si el problema persiste, crea un nuevo proyecto en Google Cloud y nuevas credenciales")

if __name__ == "__main__":
    main()
