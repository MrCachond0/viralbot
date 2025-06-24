import json
import os
from datetime import datetime

class PostTracker:
    """
    Clase para hacer seguimiento de los posts ya utilizados y evitar duplicados.
    """
    def __init__(self, history_file='posts_history.json'):
        self.history_file = history_file
        self.posts_history = self._load_history()

    def _load_history(self):
        """Carga el historial de posts desde el archivo"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error al leer el archivo {self.history_file}, creando nuevo historial")
                return {"posts": [], "subreddits": {}}
        else:
            return {"posts": [], "subreddits": {}}

    def _save_history(self):
        """Guarda el historial de posts en el archivo"""
        with open(self.history_file, 'w') as f:
            json.dump(self.posts_history, f, indent=2)

    def is_post_used(self, post_id):
        """Verifica si un post ya ha sido utilizado"""
        return post_id in self.posts_history["posts"]

    def add_post(self, post_id, subreddit, title, url=None):
        """Añade un post al historial"""
        if post_id not in self.posts_history["posts"]:
            self.posts_history["posts"].append(post_id)
            
            # Registrar también en el historial por subreddit
            if subreddit not in self.posts_history["subreddits"]:
                self.posts_history["subreddits"][subreddit] = []
            
            # Añadir detalles del post
            post_data = {
                "id": post_id,
                "title": title,
                "url": url,
                "date_used": datetime.now().isoformat()
            }
            
            self.posts_history["subreddits"][subreddit].append(post_data)
            self._save_history()
            return True
        return False

    def get_subreddit_stats(self):
        """Obtiene estadísticas de uso por subreddit"""
        stats = {}
        for subreddit, posts in self.posts_history["subreddits"].items():
            stats[subreddit] = len(posts)
        return stats

    def get_total_posts_used(self):
        """Obtiene el número total de posts utilizados"""
        return len(self.posts_history["posts"])
