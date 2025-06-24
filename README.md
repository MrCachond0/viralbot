# Reddit Shorts Bot 🚀

Un bot automatizado que genera videos en formato vertical (estilo TikTok/Shorts) a partir de posts virales de Reddit, les añade narración por texto a voz, y los sube automáticamente a YouTube.

## 🌟 Nuevas características

- **Multi-subreddit**: Extrae contenido de múltiples subreddits configurables
- **Sin repeticiones**: Realiza seguimiento de posts ya utilizados para evitar duplicados
- **Optimizado para viralidad**: Selección inteligente de contenido con mayor potencial
- **Gestión de cuotas**: Respeta los límites de la API de YouTube para evitar bloqueos
- **Operación 24/7**: Programación automática para funcionamiento continuo
- **Diversificación de contenido**: Variedad de subreddits y tipos de contenido
- **Logs detallados**: Seguimiento de operación para identificar problemas

## 🔄 Uso

### Modo simple (un solo video)

Para generar y subir un video:

```
python bot.py
```

Para generar un video sin subirlo a YouTube:

```
python bot.py --no-upload
```

### Modo continuo (24/7) - NUEVO

Para ejecutar el bot en modo continuo, respetando las cuotas de API:

```
python run_continuous.py
```

Con opciones avanzadas:

```
python run_continuous.py --max-daily 5 --initial-delay 30
```

Opciones disponibles:
- `--max-daily X`: Número máximo de videos por día (predeterminado: 5)
- `--initial-delay X`: Tiempo de espera inicial en minutos (predeterminado: 0)
- `--no-upload`: Solo genera videos sin subirlos

## 📊 Personalización

Puedes modificar el archivo `content_config.json` (se genera automáticamente) para:
- Añadir/eliminar subreddits
- Cambiar los pesos de cada subreddit (más peso = más probabilidad)
- Configurar filtros de tiempo preferidos

## Solución al Error 403: access_denied

Si estás recibiendo el error "403: access_denied" al intentar obtener los tokens de YouTube, hay varias formas de solucionarlo:

### Opción 1: Configurar Usuarios de Prueba (Recomendado)

Ejecuta el script de configuración de usuarios de prueba:

```
python configurar_usuarios_prueba.py
```

Este script te guiará para agregar tu cuenta como "usuario de prueba" en el proyecto de Google Cloud, lo que debería resolver el error 403.

### Opción 2: Método Alternativo de Autenticación

Si la opción 1 no funciona, puedes probar un método alternativo de autenticación:

```
python metodo_alternativo_tokens.py
```

Este script utiliza un enfoque diferente para la autenticación OAuth que puede funcionar mejor en algunos casos.

### Opción 3: Generar Videos Sin Subir a YouTube

Si solo quieres probar la generación de videos sin preocuparte por la subida a YouTube:

```
python bot.py --no-upload
```

Esto generará el video localmente sin intentar subirlo a YouTube.

### Opción 4: Configuración Manual

Para una guía detallada sobre cómo configurar correctamente tu proyecto de Google Cloud:

1. Lee el archivo `solucion_error_oauth.md`
2. Sigue los pasos detallados para configurar la pantalla de consentimiento, agregar usuarios de prueba y habilitar la API

## 📝 Logs

Los logs del bot en modo continuo se guardan en:
- `bot_scheduler.log`: Operaciones normales
- `bot_errors.log`: Errores y excepciones

## 🛠 Archivos principales

- `bot.py`: Núcleo del bot para generar y subir un video
- `run_continuous.py`: NUEVO - Ejecuta el bot en modo continuo
- `post_tracker.py`: NUEVO - Gestiona el historial de posts para evitar repeticiones
- `quota_manager.py`: NUEVO - Administra las cuotas de la API de YouTube
- `content_diversifier.py`: NUEVO - Optimiza la selección de contenido viral
- `bot_scheduler.py`: NUEVO - Controla la programación y ejecución continua
- `get_youtube_tokens.py`: Configura la autenticación de YouTube
- `configurar_usuarios_prueba.py`: Ayuda a configurar usuarios de prueba en Google Cloud
- `metodo_alternativo_tokens.py`: Método alternativo para obtener tokens de YouTube
- `check_youtube_setup.py`: Diagnóstico de la configuración de YouTube
- `solucion_error_oauth.md`: Guía detallada para resolver el error 403
- `youtube_troubleshooting.md`: Guía general de solución de problemas de YouTube

## 📈 Monetización

Para maximizar el potencial de monetización:

1. Comienza con los videos en modo privado para evaluar su rendimiento
2. Una vez confirmes que funcionan bien, cambia a modo público modificando la línea en `bot.py`:
   ```python
   privacy_status='public'  # Cambiar de 'private' a 'public'
   ```
3. Asegúrate de cumplir los requisitos de monetización de YouTube:
   - 1,000+ suscriptores
   - 4,000+ horas de visualización en los últimos 12 meses

## Requisitos

- Python 3.6 o superior
- Credenciales de Reddit (en .env)
- Credenciales de OAuth de Google (client_secret.json)
- Canal de YouTube
- Paquetes: praw, pyttsx3, moviepy, google-api-python-client, etc.

## Configuración

1. Copia `.env.example` a `.env` y completa las variables
2. Descarga `client_secret.json` desde Google Cloud Console
3. Ejecuta `get_youtube_tokens.py` para obtener los tokens
4. Ejecuta `bot.py` para generar y subir videos

## ⚠️ Notas importantes

- Este bot está diseñado para uso personal/educativo
- Respeta los términos de servicio de Reddit y YouTube
- No publiques contenido ofensivo o que infrinja derechos de autor
- Considera dar crédito a los creadores originales de Reddit
