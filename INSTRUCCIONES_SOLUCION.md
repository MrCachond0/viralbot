# Pasos para Solucionar el Error 403: access_denied

Hola, he creado varias soluciones para resolver el error "403: access_denied" que estás experimentando. A continuación te indico cómo proceder:

## Solución Paso a Paso:

### Opción 1: Añadir tu cuenta como "Usuario de Prueba" (Recomendado)

1. Ejecuta este script para configurar tu cuenta como usuario de prueba:
   ```
   python configurar_usuarios_prueba.py
   ```

2. Sigue las instrucciones en pantalla para añadir tu correo electrónico como usuario de prueba en la consola de Google Cloud.

3. Una vez añadido, ejecuta el script mejorado para obtener los tokens:
   ```
   python get_youtube_tokens.py
   ```

4. Cuando aparezca la pantalla de autorización, asegúrate de:
   - Hacer clic en "Avanzado" cuando veas el aviso de "Google no ha verificado esta aplicación"
   - Luego hacer clic en "Ir a [Nombre del proyecto] (no seguro)"
   - Aceptar todos los permisos solicitados

### Opción 2: Usar un Método Alternativo de Autenticación

Si la Opción 1 no funciona, prueba este método alternativo:

1. Ejecuta el siguiente script:
   ```
   python metodo_alternativo_tokens.py
   ```

2. Este script utiliza un enfoque diferente que puede evitar el error 403.

### Opción 3: Generar Videos Sin Subir a YouTube

Si solo quieres probar que el bot funciona correctamente para la generación de videos:

1. Ejecuta el bot con la opción `--no-upload`:
   ```
   python bot.py --no-upload
   ```

2. Esto generará el video localmente sin intentar subirlo a YouTube.

## Documentación Adicional

He creado varios documentos de ayuda:

- `solucion_error_oauth.md`: Guía detallada para resolver el error 403
- `youtube_troubleshooting.md`: Guía general de solución de problemas de YouTube
- `README.md`: Instrucciones generales del bot

## ¿Qué Hacer Ahora?

Te recomiendo seguir estos pasos en orden:

1. Primero ejecuta `configurar_usuarios_prueba.py` y añade tu cuenta como usuario de prueba
2. Luego ejecuta `get_youtube_tokens.py` para obtener los tokens de autenticación
3. Si eso no funciona, prueba con `metodo_alternativo_tokens.py`
4. Si aún tienes problemas, usa `python bot.py --no-upload` para al menos probar la generación de videos

Una vez que hayas resuelto el problema de autenticación, podrás usar el bot normalmente con:
```
python bot.py
```

Esto generará y subirá automáticamente videos de Reddit a YouTube.

¡Espero que estas soluciones te ayuden a resolver el problema!
