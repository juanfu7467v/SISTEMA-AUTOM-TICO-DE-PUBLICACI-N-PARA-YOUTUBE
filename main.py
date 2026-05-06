import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from src.analytics.job_runner import run_autonomous_job

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Servidor Flask para Fly.io
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Sistema Automático YouTube El Tío Jota Activo", 200

@app.route('/keep-alive', methods=['GET'])
def keep_alive():
    """
    Endpoint para mantener la máquina despierta durante procesos pesados.
    """
    return jsonify({"status": "alive"}), 200

@app.route('/start-autonomous-job', methods=['POST', 'GET'])
def start_job():
    """
    Endpoint llamado cada 5 horas para iniciar el proceso autónomo.
    """
    logger.info("Recibida petición para iniciar el job autónomo.")
    result, status_code = run_autonomous_job()
    return jsonify(result), status_code

def main():
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Iniciando servidor Flask en el puerto {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
