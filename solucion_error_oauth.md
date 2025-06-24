# Solución al Error 403: access_denied en OAuth de YouTube

Este documento te guiará para resolver el error "403: access_denied" que ocurre al intentar autorizar tu aplicación para acceder a YouTube.

## Causa del Problema

El error ocurre porque Google impone restricciones a las aplicaciones OAuth que no están verificadas. Cuando intentas obtener permisos para subir videos a YouTube (que es un permiso sensible), Google muestra una pantalla de advertencia y restringe el acceso a usuarios que no estén registrados como "usuarios de prueba".

## Solución Paso a Paso

### 1. Configurar la Pantalla de Consentimiento de OAuth

1. Ve a la [Consola de Google Cloud](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. En el menú lateral, selecciona **APIs y servicios** > **Pantalla de consentimiento de OAuth**
4. Si no has configurado la pantalla de consentimiento, selecciona el tipo **Externo** y haz clic en **Crear**
5. Completa la información necesaria:
   - **Nombre de la aplicación**: "Reddit Shorts Bot" (o el nombre que prefieras)
   - **Correo electrónico de asistencia**: tu correo electrónico
   - **Logotipo**: opcional
   - **Dominio de la aplicación**: puedes omitir esto
   - **Correos electrónicos de contacto del desarrollador**: tu correo electrónico
6. Haz clic en **Guardar y continuar**

### 2. Agregar Ámbitos (Scopes)

1. En la sección de **Ámbitos**, haz clic en **Añadir o quitar ámbitos**
2. Busca y selecciona los siguientes ámbitos:
   - `https://www.googleapis.com/auth/youtube.upload` (para subir videos)
   - `https://www.googleapis.com/auth/youtube.force-ssl` (para otras operaciones)
3. Haz clic en **Actualizar** y luego en **Guardar y continuar**

### 3. Agregar Usuarios de Prueba

Este es el paso más importante para resolver el error 403:

1. En la sección de **Usuarios de prueba**, haz clic en **+ Añadir usuarios**
2. Agrega tu correo electrónico de Google (el mismo que usas para YouTube)
3. Puedes agregar hasta 100 usuarios de prueba
4. Haz clic en **Guardar y continuar**
5. Completa el resto del asistente y haz clic en **Volver al panel**

### 4. Habilitar la API de YouTube

1. En el menú lateral, selecciona **APIs y servicios** > **Biblioteca**
2. Busca "YouTube Data API v3"
3. Haz clic en ella y luego en **Habilitar**

### 5. Verificar las Credenciales OAuth

1. En el menú lateral, selecciona **APIs y servicios** > **Credenciales**
2. Busca tu "ID de cliente de OAuth 2.0" existente y haz clic en el icono de edición (lápiz)
3. Asegúrate de que el tipo sea **Aplicación de escritorio**
4. Verifica que las URIs de redirección incluyan `http://localhost`
5. Haz clic en **Guardar**
6. **Opcional**: Si quieres empezar desde cero, puedes eliminar las credenciales existentes y crear nuevas

### 6. Descargar las Nuevas Credenciales

1. Haz clic en el ID de cliente de OAuth 2.0
2. Haz clic en **Descargar JSON**
3. Guarda el archivo como `client_secret.json` en la carpeta de tu proyecto, reemplazando el archivo existente

### 7. Ejecutar el Script Nuevamente

Ahora ejecuta el script `get_youtube_tokens.py` nuevamente:

```
python get_youtube_tokens.py
```

### 8. En la Pantalla de Consentimiento

Cuando se abra la pantalla de autorización en tu navegador:

1. Asegúrate de iniciar sesión con la misma cuenta que agregaste como usuario de prueba
2. Verás una advertencia que dice "Google no ha verificado esta aplicación"
3. Haz clic en **Continuar** (o similar)
4. En la siguiente pantalla, verás los permisos que solicita la aplicación
5. Haz clic en **Continuar** (o "Permitir")

## Solución Alternativa: Usar Menos Permisos

Si solo necesitas crear videos localmente sin subirlos a YouTube, puedes modificar el script para que no solicite permisos de YouTube. Para hacer esto, ejecuta el bot con la opción `--no-upload`:

```
python bot.py --no-upload
```

Esto solo generará el video localmente sin intentar subirlo a YouTube.

## Otras Consideraciones

- **Verificación de la aplicación**: Para un uso a largo plazo, considera [verificar tu aplicación con Google](https://support.google.com/cloud/answer/7454865)
- **Cuotas de API**: La API de YouTube tiene límites diarios. Para una aplicación no verificada, estos límites son bajos
- **Caducidad de tokens**: Los tokens de acceso caducan. El script está diseñado para renovarlos automáticamente usando el token de actualización

Si sigues teniendo problemas después de seguir estos pasos, contacta al soporte de Google Cloud o considera utilizar un enfoque diferente para la subida de videos.
