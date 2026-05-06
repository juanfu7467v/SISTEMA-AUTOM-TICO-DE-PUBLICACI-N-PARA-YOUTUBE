import os
import logging
import requests
import threading
import time
import sys
from datetime import datetime
from src.analytics.google_youtube_trends import get_validated_trends
from src.analytics.ai_analyzer import analyze_trends_and_recommend
from src.analytics.channel_config import get_channel_config
from src.analytics.state_manager import get_next_channel_to_analyze
from src.utils.github_storage import save_to_github_json

logger = logging.getLogger(__name__)

def run_autonomous_job():
    """
    Inicia el proceso autónomo en un hilo separado.
    """
    job_thread = threading.Thread(target=_job_execution)
    job_thread.start()
    return {"status": "Job de análisis profundo iniciado en background"}, 202

def _send_keep_alive():
    """
    Envía peticiones al endpoint /keep-alive para evitar que la máquina se duerma durante el trabajo.
    """
    port = os.getenv("PORT", "8080")
    url = f"http://localhost:{port}/keep-alive"
    while getattr(threading.current_thread(), "do_run", True):
        try:
            requests.get(url, timeout=5)
            logger.debug("Keep-alive enviado.")
        except Exception:
            pass
        time.sleep(60) # Cada minuto

def _job_execution():
    """
    Ejecución del job autónomo.
    """
    logger.info("=" * 80)
    logger.info("Iniciando ejecución del job autónomo (activado por petición externa)")
    logger.info("=" * 80)

    # Iniciar hilo de keep-alive
    keep_alive_thread = threading.Thread(target=_send_keep_alive)
    keep_alive_thread.do_run = True
    keep_alive_thread.start()

    target_url = os.getenv("TARGET_URL", "https://crear-videos-subir-youtuve.fly.dev/trigger-video")

    # Determinar qué canal analizar (rotación automática)
    channel_name = get_next_channel_to_analyze()
    
    # Obtener configuración del canal
    channel_config = get_channel_config(channel_name)
    if not channel_config:
        logger.error(f"No se encontró configuración para el canal: {channel_name}")
        logger.info("=" * 80)
        _stop_keep_alive_and_shutdown(keep_alive_thread)
        return
    
    channel_id = channel_config.get("id")
    logger.info(f"Analizando canal: {channel_name} (ID: {channel_id})")

    try:
        # 1. Analizar tendencias con Google Trends y validar con YouTube Search
        logger.info(f"Obteniendo tendencias de YouTube para {channel_name}...")
        trends = get_validated_trends(channel_id=channel_id)
        if not trends:
            logger.error(f"No se pudieron obtener las tendencias de YouTube para {channel_name}.")
            return

        # 2. Generar recomendaciones profundas usando OpenAI
        logger.info(f"Generando recomendaciones profundas para {channel_name}...")
        recommendation = analyze_trends_and_recommend(trends, channel_name=channel_name)
        if not recommendation:
            logger.error(f"No se pudo generar la recomendación profunda para {channel_name}.")
            return

        # Asegurar campos requeridos
        recommendation["canal_objetivo"] = channel_name
        recommendation["fecha_analisis"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Guardar el resultado en data.json
        logger.info(f"Guardando resultado del análisis para {channel_name}...")
        save_success = save_to_github_json(recommendation)
        if save_success:
            logger.info(f"✓ Resultado del análisis para {channel_name} guardado exitosamente en GitHub.")
        else:
            logger.warning(f"⚠ No se pudo guardar el resultado para {channel_name} en GitHub.")

        # 4. Enviar el JSON al servidor externo
        try:
            logger.info(f"Enviando recomendación para {channel_name} a {target_url}...")
            response = requests.post(target_url, json=recommendation, timeout=60)
            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Recomendación para {channel_name} enviada con éxito: {response.status_code}")
            else:
                logger.error(f"✗ Error al enviar recomendación para {channel_name}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"✗ Error en la petición HTTP al servidor de destino para {channel_name}: {e}")

        logger.info(f"✓ Análisis de {channel_name} completado exitosamente.")
        logger.info("Proceso finalizado. Apagando sistema para ahorrar recursos...")

    except Exception as e:
        logger.error(f"Error inesperado durante la ejecución del job: {e}")
    
    finally:
        logger.info("=" * 80)
        _stop_keep_alive_and_shutdown(keep_alive_thread)

def _stop_keep_alive_and_shutdown(thread):
    """Detiene el keep-alive y apaga el sistema."""
    thread.do_run = False
    _shutdown_system()

def _shutdown_system():
    """
    Intenta detener la máquina o el proceso de forma segura.
    """
    logger.info("Iniciando secuencia de apagado automático...")
    time.sleep(5)
    os._exit(0)
