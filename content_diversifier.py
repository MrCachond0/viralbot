import random
import praw
import json
import os
from datetime import datetime

class ContentDiversifier:
    """
    Clase para diversificar y optimizar la selección de contenido para maximizar 
    el potencial viral.
    """
    # Lista de subreddits populares con buen contenido para shorts
    DEFAULT_SUBREDDITS = [
        "Showerthoughts",
        "LifeProTips",
        "AskReddit",
        "explainlikeimfive",
        "todayilearned",
        "YouShouldKnow",
        "TrueOffMyChest",
        "confessions",
        "unpopularopinion",
        "TIFU"
    ]
    
    # Mapeo de subreddits a tipos de contenido para etiquetas/títulos
    SUBREDDIT_CATEGORIES = {
        "Showerthoughts": ["thoughts", "mind-blowing", "reflection"],
        "LifeProTips": ["tips", "advice", "life-hack"],
        "AskReddit": ["question", "story", "opinion"],
        "explainlikeimfive": ["explanation", "simple", "educational"],
        "todayilearned": ["fact", "interesting", "educational"],
        "YouShouldKnow": ["important", "knowledge", "advice"],
        "TrueOffMyChest": ["confession", "personal", "story"],
        "confessions": ["confession", "secret", "personal"],
        "unpopularopinion": ["controversial", "opinion", "debate"],
        "TIFU": ["mistake", "story", "embarrassing"]
    }
    
    def __init__(self, config_file='content_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self):
        """Carga la configuración desde el archivo"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error al leer el archivo {self.config_file}, usando configuración predeterminada")
                return self._get_default_config()
        else:
            # Crear configuración inicial
            config = self._get_default_config()
            self._save_config(config)
            return config
    
    def _get_default_config(self):
        """Obtiene la configuración predeterminada"""
        return {
            "active_subreddits": self.DEFAULT_SUBREDDITS,
            "subreddit_weights": {sr: 10 for sr in self.DEFAULT_SUBREDDITS},
            "time_filters": ["day", "week"],
            "time_filter_weights": {"day": 70, "week": 30},
            "post_count": 5,  # Número de posts a obtener para seleccionar el mejor
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_config(self, config=None):
        """Guarda la configuración en el archivo"""
        if config is None:
            config = self.config
        
        # Actualizar fecha
        config["last_updated"] = datetime.now().isoformat()
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def add_subreddit(self, subreddit, weight=10):
        """Añade un nuevo subreddit a la lista activa"""
        if subreddit not in self.config["active_subreddits"]:
            self.config["active_subreddits"].append(subreddit)
            self.config["subreddit_weights"][subreddit] = weight
            self._save_config()
            return True
        return False
    
    def remove_subreddit(self, subreddit):
        """Elimina un subreddit de la lista activa"""
        if subreddit in self.config["active_subreddits"]:
            self.config["active_subreddits"].remove(subreddit)
            if subreddit in self.config["subreddit_weights"]:
                del self.config["subreddit_weights"][subreddit]
            self._save_config()
            return True
        return False
    
    def update_subreddit_weight(self, subreddit, weight):
        """Actualiza el peso de un subreddit"""
        if subreddit in self.config["active_subreddits"]:
            self.config["subreddit_weights"][subreddit] = weight
            self._save_config()
            return True
        return False
    
    def select_random_subreddit(self):
        """Selecciona un subreddit aleatorio basado en los pesos configurados"""
        # Crear lista ponderada
        weighted_list = []
        for sr in self.config["active_subreddits"]:
            weight = self.config["subreddit_weights"].get(sr, 10)
            weighted_list.extend([sr] * weight)
        
        if not weighted_list:
            return random.choice(self.DEFAULT_SUBREDDITS)
        
        return random.choice(weighted_list)
    
    def select_time_filter(self):
        """Selecciona un filtro de tiempo aleatorio basado en los pesos configurados"""
        # Crear lista ponderada
        weighted_list = []
        for tf in self.config["time_filters"]:
            weight = self.config["time_filter_weights"].get(tf, 10)
            weighted_list.extend([tf] * weight)
        
        if not weighted_list:
            return "day"
        
        return random.choice(weighted_list)
    
    def get_post_tags(self, subreddit):
        """Obtiene etiquetas relevantes para un subreddit específico"""
        if subreddit in self.SUBREDDIT_CATEGORIES:
            # Combinar etiquetas específicas con generales
            tags = self.SUBREDDIT_CATEGORIES[subreddit] + ["shorts", "viral", "reddit"]
            # Agregar el nombre del subreddit como etiqueta
            tags.append(subreddit.lower())
            return tags
        else:
            return ["shorts", "viral", "reddit", subreddit.lower()]
    
    def generate_video_title(self, post_title, subreddit):
        """Genera un título optimizado para YouTube basado en el post original"""
        # Opciones de prefijos para diferentes subreddits
        prefix_options = {
            "Showerthoughts": ["Mind-blowing thought: ", "Ever wondered: ", "Shower thought: "],
            "LifeProTips": ["Pro Tip: ", "Life Hack: ", "Must-know tip: "],
            "AskReddit": ["Question: ", "People asked: ", "Reddit responds: "],
            "explainlikeimfive": ["Simply explained: ", "Easy to understand: ", "ELI5: "],
            "todayilearned": ["Amazing fact: ", "Did you know? ", "TIL: "],
            "YouShouldKnow": ["You need to know: ", "Important: ", "YSK: "],
            "TrueOffMyChest": ["Confession: ", "Had to share: ", "True story: "],
            "confessions": ["Secret revealed: ", "Anonymous confession: ", "They admitted: "],
            "unpopularopinion": ["Controversial opinion: ", "Hot take: ", "Unpopular: "],
            "TIFU": ["Epic fail: ", "Big mistake: ", "TIFU: "]
        }
        
        # Seleccionar un prefijo aleatorio o uno genérico
        if subreddit in prefix_options:
            prefix = random.choice(prefix_options[subreddit])
        else:
            prefix = random.choice(["Trending: ", "Viral: ", "You won't believe: ", ""])
        
        # Formatear el título
        # Si el título ya es corto, usar completo; si no, acortar
        if len(post_title) <= 80:
            return f"{prefix}{post_title}"
        else:
            # Acortar a ~80 caracteres y añadir elipsis
            return f"{prefix}{post_title[:77]}..."
