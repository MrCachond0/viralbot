import os
import sys
import json
import webbrowser
import time
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

def get_project_id():
    """Obtiene el ID del proyecto desde client_secret.json"""
    if not os.path.exists("client_secret.json"):
        print_error("No se encontró el archivo client_secret.json")
        return None
    
    try:
        with open("client_secret.json", "r") as f:
            data = json.load(f)
        
        if "installed" in data and "project_id" in data["installed"]:
            return data["installed"]["project_id"]
        elif "web" in data and "project_id" in data["web"]:
            return data["web"]["project_id"]
        else:
            print_warning("No se pudo encontrar el ID del proyecto en client_secret.json")
            return None
    except Exception as e:
        print_error(f"Error al leer client_secret.json: {str(e)}")
        return None

def main():
    print_header("CONFIGURADOR DE USUARIOS DE PRUEBA PARA OAUTH")
    
    # Obtener el ID del proyecto
    project_id = get_project_id()
    if not project_id:
        print_error("No se pudo determinar el ID del proyecto.")
        print("Por favor, verifica que tienes un archivo client_secret.json válido.")
        sys.exit(1)
    
    print_success(f"ID del proyecto: {project_id}")
    
    # Instrucciones para configurar usuarios de prueba
    print_step(1, "Instrucciones para agregar usuarios de prueba")
    print(f"Para solucionar el error 403 'access_denied', debes agregar tu cuenta como usuario de prueba.")
    print("Sigue estos pasos:")
    print("1. Abre la página de configuración de la Pantalla de consentimiento de OAuth")
    print("2. Ve a la sección 'Usuarios de prueba'")
    print("3. Haz clic en '+ Añadir usuarios'")
    print("4. Agrega tu correo electrónico de Google (el mismo que usas para YouTube)")
    print("5. Haz clic en 'Guardar'")
    
    # Preguntar si quiere abrir la página de configuración
    print()
    open_browser = input("¿Quieres abrir la página de configuración ahora? (s/n): ").lower().startswith("s")
    
    if open_browser:
        # URL de la pantalla de consentimiento OAuth
        url = f"https://console.cloud.google.com/apis/credentials/consent?project={project_id}"
        
        print_warning("Abriendo navegador... Si no se abre automáticamente, visita esta URL:")
        print(url)
        
        # Intentar abrir el navegador
        try:
            webbrowser.open(url)
        except Exception as e:
            print_error(f"No se pudo abrir el navegador: {str(e)}")
            print("Por favor, visita manualmente la URL anterior.")
    
    print()
    print_step(2, "Verificación")
    print("Una vez que hayas agregado tu cuenta como usuario de prueba:")
    print("1. Vuelve a ejecutar el script get_youtube_tokens.py")
    print("2. Cuando se abra la pantalla de autorización:")
    print("   - Haz clic en 'Avanzado' o 'Configuración'")
    print("   - Luego haz clic en 'Ir a [Nombre de tu proyecto] (no seguro)'")
    print("   - Asegúrate de ACEPTAR todos los permisos solicitados")
    
    print()
    print_step(3, "Solución alternativa")
    print("Si prefieres probar el bot sin subir videos a YouTube:")
    print("1. Ejecuta el bot con la opción --no-upload:")
    print("   python bot.py --no-upload")
    print("2. Esto generará el video localmente sin intentar subirlo a YouTube")
    
    print()
    print_header("RESUMEN")
    print("1. Agrega tu cuenta como usuario de prueba en la consola de Google Cloud")
    print("2. Ejecuta get_youtube_tokens.py y acepta los permisos")
    print("3. Ejecuta bot.py para generar y subir videos")
    print("4. Si sigues teniendo problemas, usa la opción --no-upload")
    
    print()
    print("Para más detalles, consulta el archivo 'solucion_error_oauth.md'")

if __name__ == "__main__":
    main()
