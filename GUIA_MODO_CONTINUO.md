# Guía de uso del bot en modo continuo 24/7

Este documento explica cómo utilizar el bot de Reddit a YouTube en modo continuo para generar ingresos pasivos a través de vistas de YouTube.

## Configuración inicial

Antes de ejecutar el bot en modo continuo, asegúrate de que:

1. Has ejecutado el bot en modo normal al menos una vez con éxito (`python bot.py`)
2. Has resuelto cualquier problema de autenticación con YouTube
3. Has verificado que los videos se suben correctamente

## Ejecutando el bot en modo continuo

El bot ahora incluye un nuevo script `run_continuous.py` que permite ejecutarlo en modo 24/7 sin intervención manual.

### Comando básico

```
python run_continuous.py
```

Este comando iniciará el bot con la configuración predeterminada:
- Máximo 5 videos por día
- Sin retraso inicial
- Subida automática a YouTube

### Opciones avanzadas

Puedes personalizar el comportamiento del bot con estas opciones:

```
python run_continuous.py --max-daily 3 --initial-delay 15
```

- `--max-daily X`: Establece el número máximo de videos a subir por día (predeterminado: 5)
- `--initial-delay X`: Añade un retraso inicial en minutos antes de la primera ejecución (predeterminado: 0)
- `--no-upload`: Solo genera videos sin subirlos a YouTube

### Ejecutando en segundo plano (Windows)

Para ejecutar el bot en segundo plano en Windows, puedes usar:

```
start /B python run_continuous.py > bot_output.log 2>&1
```

## Archivos de seguimiento

El bot en modo continuo genera dos archivos de log:

- `bot_scheduler.log`: Registra todas las operaciones normales
- `bot_errors.log`: Registra solo errores y excepciones

Estos archivos son útiles para diagnosticar problemas si el bot deja de funcionar.

## Archivos de estado

El bot también genera varios archivos JSON que mantienen el estado entre ejecuciones:

- `posts_history.json`: Registro de todos los posts de Reddit ya utilizados
- `quota_stats.json`: Seguimiento del uso de cuota de la API de YouTube
- `content_config.json`: Configuración de subreddits y pesos

Puedes editar manualmente `content_config.json` para ajustar la configuración de subreddits.

## Optimización para ingresos

Para maximizar los ingresos pasivos:

1. Al principio, verifica manualmente la calidad de los videos generados
2. Una vez que estés satisfecho con el rendimiento, cambia el modo de privacidad a público:
   - Edita `bot.py` y cambia `privacy_status='private'` a `privacy_status='public'`

3. Ejecuta el bot en modo continuo:
   ```
   python run_continuous.py --max-daily 4
   ```

4. Monitorea el rendimiento de los videos en YouTube Studio
5. Ajusta el número de videos diarios según el rendimiento (empieza con menos y aumenta gradualmente)

## Consejos importantes

- **No excedas la cuota diaria**: YouTube tiene un límite de 10,000 unidades de cuota por día. Cada subida consume aproximadamente 1,600 unidades.
- **Diversifica el contenido**: El bot ahora selecciona de múltiples subreddits para mantener variedad.
- **Sé paciente**: La monetización de YouTube requiere 1,000 suscriptores y 4,000 horas de visualización.
- **Mejora con el tiempo**: Revisa qué videos obtienen más vistas y ajusta la configuración para enfocarte en ese tipo de contenido.

## Solución de problemas comunes

### El bot se detiene inesperadamente

1. Revisa `bot_errors.log` para identificar la causa
2. Verifica que las credenciales de YouTube siguen siendo válidas
3. Asegúrate de tener suficiente espacio en disco

### Los videos no se suben correctamente

1. Ejecuta `check_youtube_setup.py` para diagnosticar problemas
2. Verifica que no has excedido la cuota diaria de la API
3. Regenera los tokens de YouTube con `get_youtube_tokens.py`

### Cuota de API agotada

Si agotas la cuota de API, el bot esperará automáticamente hasta el siguiente día. No necesitas hacer nada manualmente.
