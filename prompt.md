## 🤖 Reddit Video Bot – Prompt para GitHub Copilot Chat

Este prompt crea un bot en Python que genera un video tipo Short/TikTok con contenido viral de Reddit, incluyendo voz y fondo animado. Ideal para proyectos rápidos que generen ingresos pasivos, ejecutable 100% desde VSCode en menos de 30 minutos.

---

### ✅ Prompt completo para GitHub Copilot Chat:

```
Crea un script en Python llamado `bot.py` que:

1. Use `PRAW` para conectarse a Reddit con claves guardadas en un archivo `.env`. Extrae el post más popular del día del subreddit `Showerthoughts`.
2. Usa la librería `pyttsx3` para convertir el título del post en una locución y guardar el audio como `audio.mp3`.
3. Usa `moviepy` para crear un video de resolución vertical (1080x1920) con fondo animado (puede ser un degradado o patrón generado) de 10 segundos.
4. Superpone el texto del post centrado en el video y sincronizado con la duración del audio.
5. Añade la locución como audio del video final.
6. Guarda el video como `output.mp4`.
7. Carga las claves de Reddit desde un archivo `.env` (variables: `CLIENT_ID`, `CLIENT_SECRET`, `USER_AGENT`).
8. Crea también un archivo `.env.example` con esas variables como plantilla.
9. Incluye un `requirements.txt` con todas las dependencias necesarias.
10. Asegúrate de que el script funcione al correr `python bot.py`.

El video debe verse profesional: texto grande, legible, centrado, con margen, fondo en movimiento simple. El bot debe funcionar de forma autónoma sin intervención adicional.
```

---

### 📁 Estructura esperada del proyecto:

```
reddit-bot/
├── bot.py
├── requirements.txt
├── .env
├── .env.example
├── audio.mp3         ← generado automáticamente
└── output.mp4        ← video final listo para subir
```

---

### 🛠️ Dependencias esperadas (requirements.txt):

```
praw
python-dotenv
pyttsx3
moviepy
```

---

### 🚀 Instrucciones de ejecución:

1. Crea tu archivo `.env` con las credenciales de Reddit:

```
CLIENT_ID=xxxx
CLIENT_SECRET=xxxx
USER_AGENT=bot_shorts_v1
```

2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta el bot:

```bash
python bot.py
```

---

Con esto, el bot generará un video vertical con voz y texto de un post viral de Reddit, listo para subir como contenido automatizado a YouTube Shorts o TikTok.

