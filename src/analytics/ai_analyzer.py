import os
import json
import logging
from src.utils.openai_manager import OpenAIManager
from src.analytics.channel_config import get_channel_config
from src.analytics.content_strategy import get_content_type_for_day, build_enhanced_recommendation

logger = logging.getLogger(__name__)

def analyze_trends_and_recommend(trends_data, channel_name=None):
    """
    Utiliza OpenAI para realizar un análisis profundo.
    """
    
    # Preparar el contexto y el prompt
    config = get_channel_config(channel_name)
    content_config = get_content_type_for_day(channel_name)
    formato_hoy = content_config.get("formato")
    
    tema_contexto = ""
    if formato_hoy == "Video largo":
        tema_contexto = """
        IMPORTANTE: Hoy toca un VIDEO LARGO. El tema DEBE estar relacionado con:
        - Análisis de Películas (crítica profunda, mensajes ocultos, lecciones de vida en el cine).
        - Análisis de personajes o guiones.
        - Relación entre cine y realidad social/filosófica.
        """
    else:
        tema_contexto = """
        IMPORTANTE: Hoy toca un SHORT. El tema DEBE ser VARIADO y DINÁMICO, alternando entre:
        - Películas (curiosidades rápidas, tops, escenas icónicas).
        - Filosofía (Estoicismo, Sócrates, Diógenes, Maquiavelo).
        - Historia (Imperio Inca, civilizaciones antiguas, grandes hitos).
        - Pensamiento crítico y reflexiones rápidas.
        EVITA repetir el mismo tema de los últimos días.
        """

    channel_context = ""
    if config:
        channel_context = f"""
        Contexto del Canal '{channel_name}':
        - Temas principales: {", ".join(config['topics'])}
        - Descripción: {config['description']}
        - Web de referencia: {config['website_promo']}
        
        {tema_contexto}
        """

    prompt = f"""
    Eres un experto estratega de contenido para YouTube. Analiza los siguientes datos:

    {channel_context}

    TENDENCIAS VALIDADAS (Google Trends + YouTube Search):
    {json.dumps(trends_data.get('validated_trends', []), indent=2)}

    DATOS ESPECÍFICOS DEL CANAL (Rendimiento y Comentarios):
    {json.dumps(trends_data.get('channel_specific', {}), indent=2)}

    TAREAS:
    1. ANALISIS PROFUNDO: Identifica qué temas del canal están funcionando mejor.
    2. ESCUCHA ACTIVA: Revisa los comentarios para detectar peticiones de la audiencia.
    3. ESTRATEGIA: Genera una recomendación de video que combine las tendencias con la esencia del canal.
    4. VARIEDAD: Asegúrate de que el tema propuesto sea diferente a los anteriores del canal.
    5. FORMATO: El formato sugerido DEBE ser '{formato_hoy}'.

    Responde ÚNICAMENTE en formato JSON válido con la siguiente estructura:
    {{
      "tema_recomendado": "Título viral y atractivo",
      "titulo": "Título viral y atractivo",
      "idea_contenido": "Descripción detallada del video, tono y estructura.",
      "formato_sugerido": "{formato_hoy}",
      "hora_optima_publicacion": "HH:MM",
      "canal": "{channel_name}",
      "categoria": "Categoría específica (ej: Cine, Filosofía, Historia, etc.)",
      "analisis_audiencia": {{
        "temas_solicitados": ["tema1", "tema2"],
        "sentimiento_general": "positivo/neutro/negativo",
        "observaciones_engagement": "Breve nota sobre el rendimiento reciente"
      }},
      "interaccion_sugerida": [
        {{
          "comentario_original": "Texto del comentario",
          "respuesta_sugerida": "Respuesta amable saludando al usuario"
        }}
      ]
    }}
    """

    def _parse_and_enrich_response(text, channel_name, formato_hoy, content_config):
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        try:
            recommendation = json.loads(clean_text)
            recommendation["canal"] = channel_name
            recommendation["formato_sugerido"] = formato_hoy
            return build_enhanced_recommendation(recommendation, content_config)
        except Exception as e:
            logger.error(f"Error al parsear JSON de OpenAI: {e}")
            return None

    try:
        logger.info(f"Generando recomendación con OpenAI para {channel_name}...")
        response_text = OpenAIManager.analyze_with_fallback(prompt)
        if response_text:
            return _parse_and_enrich_response(response_text, channel_name, formato_hoy, content_config)
        else:
            logger.error("OpenAI no devolvió ninguna respuesta.")
            return None

    except Exception as e:
        logger.error(f"Error crítico en el análisis de IA: {e}")
        return None
