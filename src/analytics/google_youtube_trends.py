import os
import logging
import json
import time
from googleapiclient.discovery import build
from datetime import datetime
from src.utils.openai_manager import OpenAIManager

logger = logging.getLogger(__name__)

def _get_youtube_search_views(query):
    """
    Busca el término en YouTube y calcula el promedio de vistas de los primeros 5 videos.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("Falta YOUTUBE_API_KEY para la validación de YouTube Search.")
        return 0

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            order="viewCount",
            maxResults=5
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        
        if not video_ids:
            logger.warning(f"No se encontraron videos en YouTube para la búsqueda: {query}")
            return 0

        videos_stats = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()

        total_views = 0
        for item in videos_stats.get("items", []):
            total_views += int(item["statistics"].get("viewCount", 0))
        
        avg_views = total_views / len(video_ids) if video_ids else 0
        logger.info(f"✓ Validación de vistas en YouTube para {query}: {avg_views:.0f} vistas promedio.")
        return avg_views

    except Exception as e:
        logger.error(f"Error al obtener vistas de YouTube para {query}: {e}")
        return 0

def _transform_title_with_ia(trend_topic):
    """
    Usa OpenAI para transformar una tendencia en un título emocional y viral.
    """
    prompt = f"""
    Actúa como un experto en marketing viral de YouTube. 
    
    TAREA: Convierte el siguiente tema en un TÍTULO ALTAMENTE VIRAL.
    
    REGLAS DE ORO:
    1. Debe generar CURIOSIDAD EXTREMA, EMOCIÓN o MISTERIO.
    2. No usar títulos genéricos.
    3. Usar estilo clickbait inteligente (sin mentir).
    4. Debe sonar como algo que el usuario NECESITA saber ahora mismo.

    TEMA A TRANSFORMAR: "{trend_topic}"

    Salida (solo el título transformado, sin comillas):
    """

    try:
        response_text = OpenAIManager.analyze_with_fallback(prompt)
        if response_text:
            return response_text.strip().replace('"', '')
        return trend_topic
    except Exception as e:
        logger.error(f"Error crítico al transformar título con IA para {trend_topic}: {e}")
        return trend_topic

def get_validated_trends(channel_id=None):
    """
    Flujo principal: Escucha Activa (Comentarios de YouTube) -> YouTube Search Validation -> IA Title Transformation.
    """
    logger.info("Iniciando detección de tendencias basada en Escucha Activa y Temas Estratégicos.")
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("Falta YOUTUBE_API_KEY para la Escucha Activa.")
        return None

    potential_topics = []
    channel_data = {"recent_performance": [], "audience_comments": []}

    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # 1. Obtener los últimos videos del canal para extraer comentarios
        if channel_id:
            logger.info(f"Extrayendo comentarios del canal: {channel_id}")
            search_response = youtube.search().list(
                channelId=channel_id,
                part="id,snippet",
                order="date",
                maxResults=5,
                type="video"
            ).execute()

            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            
            if video_ids:
                videos_stats = youtube.videos().list(
                    part="snippet,statistics",
                    id=",".join(video_ids)
                ).execute()

                for v in videos_stats.get("items", []):
                    v_id = v["id"]
                    stats = v["statistics"]
                    snippet = v["snippet"]
                    
                    channel_data["recent_performance"].append({
                        "title": snippet["title"],
                        "views": stats.get("viewCount", 0),
                        "likes": stats.get("likeCount", 0)
                    })

                    try:
                        comments_response = youtube.commentThreads().list(
                            part="snippet",
                            videoId=v_id,
                            maxResults=20,
                            order="relevance"
                        ).execute()

                        for c in comments_response.get("items", []):
                            comment_text = c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                            channel_data["audience_comments"].append(comment_text)
                    except Exception as ce:
                        logger.warning(f"No se pudieron obtener comentarios para el video {v_id}: {ce}")

        # 2. Usar IA para identificar temas sugeridos o temas estratégicos
        logger.info("Generando temas estratégicos y analizando comentarios con OpenAI...")
        
        prompt_topics = f"""
        Genera una lista de 8 temas potenciales para videos de YouTube.
        
        REQUISITOS:
        1. Incluye temas de PELÍCULAS (análisis, curiosidades, cine actual).
        2. Incluye temas de FILOSOFÍA (Estoicismo, Sócrates, Diógenes, Maquiavelo).
        3. Incluye temas de HISTORIA (Imperio Inca, civilizaciones antiguas, misterios históricos).
        4. Considera estos comentarios y rendimiento reciente:
        
        RENDIMIENTO RECIENTE:
        {json.dumps(channel_data['recent_performance'], indent=2)}
        
        COMENTARIOS DE LA AUDIENCIA:
        {json.dumps(channel_data['audience_comments'][:50], indent=2)}
        
        Responde ÚNICAMENTE con una lista de 8 temas cortos, uno por línea.
        """

        response_text = OpenAIManager.analyze_with_fallback(prompt_topics)
        if response_text:
            extracted_topics = response_text.strip().split('\n')
            potential_topics = [t.strip('- ').strip() for t in extracted_topics if t.strip()]
            logger.info(f"✓ Temas potenciales generados: {potential_topics}")

    except Exception as e:
        logger.error(f"Error en el proceso de detección de temas: {e}")

    # Fallback si falla la IA
    if not potential_topics:
        potential_topics = ["Análisis de películas 2024", "Filosofía para la vida", "Historia del Imperio Inca", "Pensamiento de Sócrates"]

    validated_trends = []
    for topic in potential_topics:
        logger.info(f"Validando tema: '{topic}'")
        avg_views = _get_youtube_search_views(topic)

        if avg_views > 100000:
            priority = "ALTA" if avg_views > 500000 else "NORMAL"
            logger.info(f"✓ Tema aprobado: '{topic}' con prioridad {priority} ({avg_views:.0f} vistas).")
            
            # Pausa para evitar rate limits
            time.sleep(1)
            
            transformed_title = _transform_title_with_ia(topic)
            logger.info(f"✓ Título viral generado: '{transformed_title}'")
            
            validated_trends.append({
                "original_topic": topic,
                "transformed_title": transformed_title,
                "avg_youtube_views": avg_views,
                "priority": priority,
                "potential_category": "estratégico"
            })
        else:
            logger.info(f"✗ Tema rechazado: '{topic}'. Vistas insuficientes ({avg_views:.0f}).")

    if not validated_trends:
        validated_trends = [{
            "original_topic": "Lecciones de Estoicismo",
            "transformed_title": "Por qué el Estoicismo es el superpoder que necesitas hoy",
            "avg_youtube_views": 150000,
            "priority": "NORMAL",
            "potential_category": "fallback"
        }]

    validated_trends.sort(key=lambda x: x["avg_youtube_views"], reverse=True)
    
    return {
        "validated_trends": validated_trends,
        "channel_specific": channel_data
    }
