import os
import json
import logging
import requests
import base64
from datetime import datetime
from src.analytics.channel_config import CHANNEL_CONFIGS

logger = logging.getLogger(__name__)

# Orden de canales para alternancia (obtenido dinámicamente de la configuración)
CHANNELS_ROTATION = sorted(CHANNEL_CONFIGS.keys(), key=lambda k: CHANNEL_CONFIGS[k]['order'])

def get_next_channel_to_analyze(filename="data.json"):
    """
    Determina qué canal debe analizarse en la próxima petición.
    
    Lógica:
    - Si data.json está vacío, comienza con el primer canal de la rotación.
    - Si el último análisis fue de un canal, analiza el siguiente en la lista CHANNELS_ROTATION.
    - Si el último análisis fue del último canal, vuelve al primero.
    
    Returns:
        str: Nombre del canal a analizar.
    """
    try:
        # Intentar obtener el historial desde GitHub
        history = _get_analysis_history(filename)
        
        if not history:
            logger.info(f"Historial vacío. Iniciando con '{CHANNELS_ROTATION[0]}'.")
            return CHANNELS_ROTATION[0]
        
        # Obtener el último análisis
        last_entry = history[-1]
        last_channel = last_entry.get("canal")
        
        logger.info(f"Último canal analizado: {last_channel}")
        
        # Determinar el siguiente canal basándose en la lista CHANNELS_ROTATION
        if last_channel in CHANNELS_ROTATION:
            current_index = CHANNELS_ROTATION.index(last_channel)
            next_index = (current_index + 1) % len(CHANNELS_ROTATION)
            next_channel = CHANNELS_ROTATION[next_index]
        else:
            # Si hay un canal desconocido, reiniciar con el primero
            next_channel = CHANNELS_ROTATION[0]
        
        logger.info(f"Próximo canal a analizar: {next_channel}")
        return next_channel
        
    except Exception as e:
        logger.error(f"Error al determinar el próximo canal: {e}")
        # Por defecto, analizar el primer canal configurado
        return CHANNELS_ROTATION[0]


def _get_analysis_history(filename="data.json"):
    """
    Obtiene el historial de análisis desde GitHub o localmente.
    
    Returns:
        list: Lista de análisis realizados
    """
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    
    # Intentar obtener desde GitHub
    if repo and token:
        try:
            url = f"https://api.github.com/repos/{repo}/contents/{filename}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                file_data = response.json()
                content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
                history = json.loads(content_decoded)
                
                if isinstance(history, list):
                    return history
                else:
                    return [history]
        except Exception as e:
            logger.warning(f"No se pudo obtener historial desde GitHub: {e}")
    
    # Fallback: intentar obtener localmente
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                history = json.load(f)
                if isinstance(history, list):
                    return history
                else:
                    return [history]
    except Exception as e:
        logger.warning(f"No se pudo obtener historial localmente: {e}")
    
    return []


def has_channel_been_analyzed_today(channel_name, filename="data.json"):
    """
    Verifica si un canal ya ha sido analizado hoy.
    NOTA: Esta función se mantiene por compatibilidad pero ya no bloquea el flujo autónomo.
    """
    try:
        history = _get_analysis_history(filename)
        today = datetime.now().strftime("%Y-%m-%d")
        
        for entry in history:
            if entry.get("canal") == channel_name and entry.get("fecha") == today:
                logger.info(f"Canal '{channel_name}' ya fue analizado hoy.")
                return True
        
        logger.info(f"Canal '{channel_name}' no ha sido analizado hoy.")
        return False
        
    except Exception as e:
        logger.error(f"Error al verificar si el canal fue analizado hoy: {e}")
        return False
