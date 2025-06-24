# Guía de Solución de Problemas para YouTube API

## Problema: Error 403 "access_denied" durante la autorización OAuth

Si estás recibiendo un error 403 "access_denied" durante el proceso de autorización de YouTube, aquí tienes algunas soluciones:

### 1. Causas comunes del error "access_denied"

- **Rechazo manual**: Es posible que hayas rechazado accidentalmente los permisos en la pantalla de autorización.
- **Proyecto mal configurado**: El proyecto en Google Cloud no tiene la API de YouTube habilitada.
- **Credenciales incorrectas**: Las credenciales OAuth no están configuradas correctamente.
- **Pantalla de consentimiento no configurada**: No has configurado la pantalla de consentimiento en Google Cloud.
- **Cuenta sin canal de YouTube**: La cuenta de Google que estás usando no tiene un canal de YouTube asociado.

### 2. Verificación y solución paso a paso

#### Paso 1: Verifica la configuración en Google Cloud

1. Ve a la [Consola de Google Cloud](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. Ve a **APIs y servicios** > **Biblioteca**
4. Busca "YouTube Data API v3" y asegúrate de que esté habilitada
5. Ve a **APIs y servicios** > **Credenciales**
6. Verifica que tengas credenciales de tipo "ID de cliente OAuth 2.0" para aplicación de escritorio
7. Ve a **APIs y servicios** > **Pantalla de consentimiento de OAuth**
8. Asegúrate de que la pantalla de consentimiento esté configurada correctamente

#### Paso 2: Comprueba que tu cuenta tenga un canal de YouTube

1. Inicia sesión en [YouTube](https://www.youtube.com/)
2. Haz clic en tu perfil en la esquina superior derecha
3. Selecciona "Tu canal"
4. Si no tienes un canal, se te pedirá crear uno. Sigue las instrucciones para crearlo.

#### Paso 3: Regenera las credenciales OAuth

1. Ve a la [Consola de Google Cloud](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. Ve a **APIs y servicios** > **Credenciales**
4. Busca tus credenciales de tipo "ID de cliente OAuth 2.0" y elimínalas
5. Crea nuevas credenciales:
   - Haz clic en **Crear credenciales** > **ID de cliente de OAuth**
   - Selecciona **Aplicación de escritorio**
   - Dale un nombre (por ejemplo, "Reddit Shorts Bot")
   - Haz clic en **Crear**
6. Descarga el archivo JSON y guárdalo como `client_secret.json` en la carpeta del proyecto

#### Paso 4: Ejecuta el diagnóstico y regenera los tokens

1. Ejecuta el script de diagnóstico:
   ```
   python check_youtube_setup.py
   ```
2. Corrige cualquier problema detectado
3. Vuelve a ejecutar el script para obtener los tokens:
   ```
   python get_youtube_tokens.py
   ```
4. Asegúrate de **ACEPTAR** todos los permisos en la pantalla de autorización

### 3. Solución alternativa: Crear un proyecto nuevo desde cero

Si continúas teniendo problemas, la solución más efectiva puede ser crear un proyecto nuevo:

1. Ve a la [Consola de Google Cloud](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita la API de YouTube Data v3
4. Configura la pantalla de consentimiento de OAuth:
   - Selecciona "Externo" como tipo de usuario
   - Completa la información requerida (nombre de la aplicación, correo de soporte, etc.)
   - En la sección de ámbitos, añade:
     - `.../auth/youtube.upload`
5. Crea nuevas credenciales de OAuth para aplicación de escritorio
6. Descarga el archivo JSON y guárdalo como `client_secret.json`
7. Ejecuta el script para obtener los tokens:
   ```
   python get_youtube_tokens.py
   ```

### 4. Consideraciones adicionales

- **Cuenta de prueba**: Si estás usando una cuenta de desarrollador, puede haber limitaciones en el acceso a las APIs
- **Límites de cuota**: Verifica que no hayas excedido los límites de cuota para la API
- **Entorno de prueba/producción**: Si estás en modo de prueba, solo cuentas verificadas podrán acceder
- **Bloqueo temporal**: Demasiados intentos fallidos pueden resultar en un bloqueo temporal

### 5. Verificación final

Una vez que hayas obtenido los tokens correctamente, ejecuta:

```
python bot.py
```

El bot debería ser capaz de subir videos a YouTube automáticamente después de generarlos.

Si necesitas asistencia adicional, puedes consultar la [documentación oficial de la API de YouTube](https://developers.google.com/youtube/v3/guides/authentication).
