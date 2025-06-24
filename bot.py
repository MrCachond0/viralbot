import os
from dotenv import load_dotenv
import praw
import pyttsx3
import numpy as np
import pickle
import json
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import random
import time
from datetime import datetime
from post_tracker import PostTracker
from quota_manager import QuotaManager
from content_diversifier import ContentDiversifier

# 1. Cargar variables de entorno
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USER_AGENT = os.getenv('USER_AGENT')

# 2. Conectarse a Reddit y extraer un post viral que no se haya usado antes
def get_viral_post(post_tracker=None, content_diversifier=None):
    # Inicializar post_tracker si no se proporciona
    if post_tracker is None:
        post_tracker = PostTracker()
    
    # Inicializar diversificador de contenido si no se proporciona
    if content_diversifier is None:
        content_diversifier = ContentDiversifier()
    
    # Crear conexión a Reddit
    reddit = praw.Reddit(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        user_agent=USER_AGENT)
    
    # Seleccionar subreddit y filtro de tiempo aleatoriamente
    subreddit_name = content_diversifier.select_random_subreddit()
    time_filter = content_diversifier.select_time_filter()
    
    print(f"Buscando en r/{subreddit_name} (filtro: {time_filter})")
    
    # Obtener subreddit
    subreddit = reddit.subreddit(subreddit_name)
    
    # Número de intentos máximos
    max_attempts = 10
    attempts = 0
    
    # Lista para almacenar posts candidatos
    candidate_posts = []
    
    # Buscar posts populares
    for post in subreddit.top(time_filter=time_filter, limit=20):
        attempts += 1
        
        # Ignorar posts que ya se han usado
        if post_tracker.is_post_used(post.id):
            continue
        
        # Ignorar posts muy cortos o muy largos
        if len(post.title) < 15 or len(post.title) > 250:
            continue
        
        # Ignorar posts con URL (probablemente imágenes o videos)
        if hasattr(post, 'url_overridden_by_dest'):
            continue
        
        # Ignorar posts NSFW
        if post.over_18:
            continue
        
        # Añadir a candidatos
        candidate_posts.append(post)
        
        # Si tenemos suficientes candidatos o hemos alcanzado el límite de intentos
        if len(candidate_posts) >= 5 or attempts >= max_attempts:
            break
    
    # Si no encontramos ningún post adecuado, probar con otro subreddit
    if not candidate_posts:
        print(f"No se encontraron posts adecuados en r/{subreddit_name}, probando otro subreddit...")
        
        # Intentar con un subreddit diferente
        alternate_subreddit = content_diversifier.select_random_subreddit()
        while alternate_subreddit == subreddit_name and len(content_diversifier.config["active_subreddits"]) > 1:
            alternate_subreddit = content_diversifier.select_random_subreddit()
        
        print(f"Probando con r/{alternate_subreddit}")
        subreddit = reddit.subreddit(alternate_subreddit)
        
        for post in subreddit.top(time_filter=time_filter, limit=10):
            # Realizar las mismas verificaciones
            if not post_tracker.is_post_used(post.id) and len(post.title) >= 15 and len(post.title) <= 250 and not post.over_18:
                candidate_posts.append(post)
                if len(candidate_posts) >= 3:
                    break
    
    # Si aún no encontramos posts adecuados, probar con AskReddit como fallback
    if not candidate_posts:
        print("No se encontraron posts adecuados, probando con AskReddit como último recurso...")
        subreddit = reddit.subreddit('AskReddit')
        
        for post in subreddit.top(time_filter='day', limit=10):
            if not post_tracker.is_post_used(post.id) and len(post.title) >= 15 and len(post.title) <= 250 and not post.over_18:
                candidate_posts.append(post)
                if len(candidate_posts) >= 3:
                    break
    
    # Si todavía no hay posts, devolver None
    if not candidate_posts:
        print("No se encontraron posts adecuados después de varios intentos.")
        return None, None, None
    
    # Seleccionar un post aleatorio de los candidatos (priorizar los primeros)
    weights = [100 - (i * 10) for i in range(len(candidate_posts))]
    selected_post = random.choices(candidate_posts, weights=weights, k=1)[0]
    
    # Registrar el post como usado
    post_tracker.add_post(
        selected_post.id, 
        selected_post.subreddit.display_name, 
        selected_post.title,
        f"https://www.reddit.com{selected_post.permalink}"
    )
    
    # Devolver información del post
    subreddit_name = selected_post.subreddit.display_name
    
    print(f"Post seleccionado de r/{subreddit_name}: {selected_post.title}")
    return selected_post.title, selected_post.id, subreddit_name

# 3. Convertir texto a voz y guardar como audio.mp3
def text_to_speech(text, filename='audio.mp3'):
    engine = pyttsx3.init()
    # Selecciona una voz en inglés si está disponible
    voices = engine.getProperty('voices')
    for v in voices:
        lang = v.languages[0].decode('utf-8') if v.languages and hasattr(v.languages[0], 'decode') else ''
        if 'en' in lang or 'English' in v.name:
            engine.setProperty('voice', v.id)
            break
    engine.save_to_file(text, filename)
    engine.runAndWait()

# 4. Crear fondo animado (degradado en movimiento)
def make_animated_bg(duration, size=(1080,1920)):
    # Un simple ColorClip como fondo
    return ColorClip(size, color=(20, 30, 50), duration=duration)

# 5. Crear video y superponer texto
def create_video(text, audio_path, output_path='output.mp4'):
    audio = AudioFileClip(audio_path)
    duration = audio.duration  # Usamos exactamente la duración del audio
    
    # Fondo simple
    bg = make_animated_bg(duration)
    
    # Crear un TextClip simple
    # Creamos una imagen en blanco con el texto
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (1080, 1920), color=(20, 30, 50))
    draw = ImageDraw.Draw(img)
    
    # Intentamos usar una fuente más grande y gruesa para mejor legibilidad
    try:
        font = ImageFont.truetype("arial.ttf", 60)  # Intenta usar Arial
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", 60)  # Intenta con otra capitalización
        except:
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)  # Intenta usar DejaVu Sans Bold
            except:
                font = ImageFont.load_default()  # Si todo falla, usa la fuente por defecto
    
    # Ajustar el texto para que quepa en el ancho (60 caracteres por línea aproximadamente)
    import textwrap
    wrapped_text = textwrap.fill(text, width=40)
    
    # Dibuja el texto centrado con sombra para mejor legibilidad
    # Primero la sombra
    draw.text((543, 963), wrapped_text, fill="black", anchor="mm", font=font)
    # Luego el texto principal
    draw.text((540, 960), wrapped_text, fill="white", anchor="mm", font=font)
    
    img_path = "temp_text.png"
    img.save(img_path)
    
    # Usar la imagen como clip
    txt_clip = ImageClip(img_path)
    txt_clip = txt_clip.with_duration(duration)
    txt_clip = txt_clip.with_position('center')
    
    # Componer video
    video = CompositeVideoClip([bg, txt_clip])
    video = video.with_audio(audio)
    video = video.with_duration(duration)
    
    # Guardar video
    video.write_videofile(output_path, fps=24)

def youtube_authenticate():
    """
    Autenticar con la API de YouTube utilizando tokens desde .env o proceso OAuth
    """
    print('Iniciando autenticación de YouTube...')
    
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    creds = None
    
    # Intentar primero con token.pickle
    if os.path.exists('token.pickle'):
        print('Usando token.pickle existente...')
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
            # Verificar si las credenciales están expiradas
            if creds and creds.expired and creds.refresh_token:
                print('Tokens expirados, renovando...')
                creds.refresh(google.auth.transport.requests.Request())
                
                # Guardar las credenciales actualizadas
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                print('Tokens renovados correctamente')
        except Exception as e:
            print(f'Error al cargar token.pickle: {str(e)}')
            creds = None
    
    # Si no hay credenciales válidas, intentar con token.json
    if not creds or not creds.valid:
        if os.path.exists('token.json'):
            print('Usando token.json existente...')
            try:
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                
                # Verificar si las credenciales están expiradas
                if creds and creds.expired and creds.refresh_token:
                    print('Tokens expirados, renovando...')
                    creds.refresh(google.auth.transport.requests.Request())
                    
                    # Guardar las credenciales actualizadas
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                    print('Tokens renovados correctamente')
            except Exception as e:
                print(f'Error al cargar token.json: {str(e)}')
                creds = None
    
    # Si aún no hay credenciales válidas, intentar con .env
    if not creds or not creds.valid:
        refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
        if refresh_token:
            print('Usando tokens desde archivo .env...')
            try:
                creds = Credentials(
                    token=os.getenv('YOUTUBE_ACCESS_TOKEN'),
                    refresh_token=refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=os.getenv('YOUTUBE_CLIENT_ID'),
                    client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
                    scopes=SCOPES
                )
                
                # Verificar si las credenciales están expiradas y refrescarlas
                if creds and creds.expired:
                    print('Tokens expirados, renovando...')
                    creds.refresh(google.auth.transport.requests.Request())
                    
                    # Actualizar el archivo .env con el nuevo token de acceso
                    with open('.env', 'r') as f:
                        lines = f.readlines()
                        
                    with open('.env', 'w') as f:
                        for line in lines:
                            if line.startswith('YOUTUBE_ACCESS_TOKEN='):
                                f.write(f'YOUTUBE_ACCESS_TOKEN={creds.token}\n')
                            else:
                                f.write(line)
                    print('Tokens renovados y guardados en .env')
            except Exception as e:
                print(f'Error al usar tokens desde .env: {str(e)}')
                creds = None
    
    # Si todavía no hay credenciales válidas, iniciar flujo OAuth desde cero
    if not creds or not creds.valid:
        print('No se encontraron credenciales válidas, iniciando flujo OAuth...')
        
        # Verificar si existe client_secret.json
        if not os.path.exists('client_secret.json'):
            print('ERROR: No se encontró client_secret.json')
            print('Por favor, ejecuta primero el script get_youtube_tokens.py')
            raise Exception("Falta archivo client_secret.json")
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Guardar las credenciales
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
            # Actualizar también el archivo .env
            with open('.env', 'r') as f:
                lines = f.readlines()
                
            with open('.env', 'w') as f:
                for line in lines:
                    if line.startswith('YOUTUBE_ACCESS_TOKEN='):
                        f.write(f'YOUTUBE_ACCESS_TOKEN={creds.token}\n')
                    elif line.startswith('YOUTUBE_REFRESH_TOKEN='):
                        f.write(f'YOUTUBE_REFRESH_TOKEN={creds.refresh_token}\n')
                    else:
                        f.write(line)
            
            print('Nuevas credenciales obtenidas y guardadas correctamente')
        except Exception as e:
            print(f'Error durante el flujo OAuth: {str(e)}')
            print('Por favor, ejecuta el script get_youtube_tokens.py para solucionar este problema')
            raise Exception("Error en autenticación OAuth")
    
    print('Autenticación de YouTube completada correctamente')
    return creds

def upload_video_to_youtube(video_path, title, description, tags=None, privacy_status="public"):
    """
    Sube un video a YouTube
    """
    print('Iniciando subida a YouTube...')
    
    if not os.path.exists(video_path):
        print(f'ERROR: El archivo de video {video_path} no existe')
        return None
    
    try:
        creds = youtube_authenticate()
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Verificar que tenemos permiso para subir videos
        try:
            channel_request = youtube.channels().list(part="id", mine=True)
            channel_response = channel_request.execute()
            
            if not channel_response.get('items'):
                print('ERROR: No se encontró un canal de YouTube asociado a esta cuenta')
                print('Asegúrate de que la cuenta tenga un canal de YouTube')
                return None
            
            # Obtener el ID del canal
            channel_id = channel_response['items'][0]['id']
            print(f'Canal de YouTube identificado: {channel_id}')
            
            # Actualizar el archivo .env con el ID del canal si no está definido
            if not os.getenv('YOUTUBE_CHANNEL_ID'):
                with open('.env', 'r') as f:
                    lines = f.readlines()
                    
                with open('.env', 'w') as f:
                    channel_id_updated = False
                    for line in lines:
                        if line.startswith('YOUTUBE_CHANNEL_ID='):
                            f.write(f'YOUTUBE_CHANNEL_ID={channel_id}\n')
                            channel_id_updated = True
                        else:
                            f.write(line)
                    if not channel_id_updated:
                        f.write(f'YOUTUBE_CHANNEL_ID={channel_id}\n')
                print('ID del canal guardado en .env')
                
        except Exception as e:
            print(f'ERROR al verificar el canal: {str(e)}')
            return None
        
        # Configurar los metadatos del video
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or ['reddit', 'shorts', 'viral', 'bot'],
                'categoryId': '22'  # 22 = People & Blogs
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Preparar la solicitud de subida
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
        
        # Iniciar la subida
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        # Subir el video con indicador de progreso
        print('Subiendo video a YouTube...')
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f'Subido {int(status.progress() * 100)}%')
        
        print(f'¡Video subido exitosamente!')
        print(f'URL del video: https://youtu.be/{response["id"]}')
        return response['id']
        
    except Exception as e:
        print(f'ERROR durante la subida a YouTube: {str(e)}')
        print('Verifica tus credenciales y permisos, y vuelve a intentarlo')
        return None

def main_bot_process(no_upload=False):
    """
    Proceso principal del bot, desde la obtención del post hasta la subida
    a YouTube.
    
    Args:
        no_upload: Si es True, solo genera el video sin subirlo
        
    Returns:
        bool: True si el proceso fue exitoso, False en caso contrario
    """
    try:
        print('=' * 60)
        print('REDDIT SHORTS BOT - GENERADOR DE VIDEOS VIRALES')
        print('=' * 60)
        
        # Inicializar los componentes necesarios
        post_tracker = PostTracker()
        quota_manager = QuotaManager()
        content_diversifier = ContentDiversifier()
        
        # Verificar si tenemos cuota disponible para subir videos
        if not no_upload and not quota_manager.can_upload():
            print("\nERROR: No hay suficiente cuota de API disponible hoy.")
            print(f"Cuota restante: {quota_manager.get_remaining_quota()} unidades")
            print(f"Necesario para subir: {QuotaManager.UPLOAD_COST} unidades")
            print("El video no se subirá a YouTube. Intenta más tarde o usa --no-upload.")
            # Convertir a modo local
            no_upload = True
        
        # 1. Obtener post viral de Reddit
        print('\n[1] Obteniendo post viral de Reddit...')
        post_text, post_id, subreddit_name = get_viral_post(post_tracker, content_diversifier)
        if not post_text or not post_id:
            print('ERROR: No se pudo obtener un post adecuado de Reddit.')
            print('Verifica tus credenciales de Reddit en el archivo .env')
            return False
        
        print(f'Post obtenido de r/{subreddit_name}: "{post_text}"')
        
        # 2. Generar audio con TTS
        print('\n[2] Generando locución...')
        audio_file = f'audio_{post_id}.mp3'
        text_to_speech(post_text, audio_file)
        if not os.path.exists(audio_file):
            print('ERROR: No se pudo generar el archivo de audio.')
            return False
        print(f'Audio generado correctamente como {audio_file}')
        
        # 3. Crear video con texto
        print('\n[3] Creando video...')
        video_file = f'output_{post_id}.mp4'
        create_video(post_text, audio_file, video_file)
        if not os.path.exists(video_file):
            print('ERROR: No se pudo generar el archivo de video.')
            return False
        print(f'Video generado correctamente como {video_file}')
        
        # 4. Subir a YouTube (solo si no se especificó --no-upload)
        if no_upload:
            print('\n[4] Omitiendo la subida a YouTube (modo --no-upload)')
            print(f'\n¡PROCESO COMPLETADO CORRECTAMENTE!')
            print(f'Video generado en: {os.path.abspath(video_file)}')
            print('Para subir el video a YouTube, ejecuta el bot sin la opción --no-upload')
            
            # Limpiar archivos temporales
            cleanup_temp_files(audio_file, keep_video=True)
            return True
        else:
            print('\n[4] Subiendo video a YouTube...')
            try:
                # Generar título optimizado y etiquetas
                youtube_title = content_diversifier.generate_video_title(post_text, subreddit_name)
                youtube_tags = content_diversifier.get_post_tags(subreddit_name)
                
                # Añadir descripción con créditos
                youtube_description = f"""
{post_text}

Este video fue creado a partir de un post de Reddit en r/{subreddit_name}.
#shorts #viral #{subreddit_name.lower()} #reddit
                """.strip()
                
                video_id = upload_video_to_youtube(
                    video_path=video_file,
                    title=youtube_title,
                    description=youtube_description,
                    tags=youtube_tags,
                    privacy_status='public'  # Usar 'private' para pruebas, 'public' para publicación real
                )
                
                if video_id:
                    # Registrar el uso de cuota
                    quota_manager.register_upload(video_id)
                    
                    print('\n¡PROCESO COMPLETADO CORRECTAMENTE!')
                    print(f'Video subido a YouTube: https://youtu.be/{video_id}')
                    
                    # Limpiar archivos temporales
                    cleanup_temp_files(audio_file, video_file)
                    
                    return True
                else:
                    print('\nEl video se generó correctamente, pero hubo problemas al subirlo a YouTube.')
                    print('Revisa el archivo youtube_troubleshooting.md o solucion_error_oauth.md para solucionar el problema.')
                    
                    # Conservar el video por si se quiere subir manualmente
                    cleanup_temp_files(audio_file, keep_video=True)
                    
                    return False
            except Exception as e:
                print(f'\nERROR al subir a YouTube: {str(e)}')
                print('El video se generó correctamente, pero no se pudo subir a YouTube.')
                print('Revisa el archivo youtube_troubleshooting.md o solucion_error_oauth.md para solucionar el problema.')
                print(f'El video está disponible localmente en: {os.path.abspath(video_file)}')
                
                # Conservar el video por si se quiere subir manualmente
                cleanup_temp_files(audio_file, keep_video=True)
                
                return False
    
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario.")
        return False
    except Exception as e:
        print(f"\nERROR inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_temp_files(audio_file, video_file=None, keep_video=False):
    """Limpia archivos temporales después de procesar un video"""
    try:
        # Siempre eliminar el audio temporal
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"Archivo temporal eliminado: {audio_file}")
        
        # Eliminar imagen de texto temporal si existe
        if os.path.exists("temp_text.png"):
            os.remove("temp_text.png")
        
        # Eliminar video solo si se especifica y no queremos conservarlo
        if video_file and not keep_video and os.path.exists(video_file):
            os.remove(video_file)
            print(f"Archivo temporal eliminado: {video_file}")
    except Exception as e:
        print(f"Error al limpiar archivos temporales: {str(e)}")

if __name__ == '__main__':
    try:
        # Procesar argumentos de línea de comandos
        import argparse
        parser = argparse.ArgumentParser(description='Bot para generar videos de Reddit y subirlos a YouTube')
        parser.add_argument('--no-upload', action='store_true', help='Solo genera el video, sin subirlo a YouTube')
        args = parser.parse_args()
        
        # Ejecutar el proceso principal
        main_bot_process(args.no_upload)
    
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario.")
    except Exception as e:
        print(f"\nERROR inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
