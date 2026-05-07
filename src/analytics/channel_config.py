import os

CHANNEL_CONFIGS = {
    "El Tío Jota": {
        "id": os.getenv("ID_CANAL", "UC_EL_TIO_JOTA_ID"),
        "topics": [
            "Análisis de películas",
            "Filosofía (estoicismo)",
            "Historia (Imperio Inca, civilizaciones antiguas)",
            "Pensadores (Sócrates, Diógenes, Maquiavelo)",
            "Crecimiento personal",
            "Motivación"
        ],
        "description": "Canal enfocado en el crecimiento personal a través del cine, la filosofía y la historia, analizando la realidad desde una perspectiva crítica y profunda.",
        "website_promo": "https://masitaprex.com/PeliPREX",
        "order": 1
    },
    "El Criterio": {
        "id": os.getenv("ID_CANAL_2", "UC_EL_CRITERIO_ID"),
        "topics": [
            "Análisis crítico de películas",
            "Cine y cultura",
            "Reflexiones filosóficas",
            "Historia y grandes pensadores",
            "Actualidad con criterio"
        ],
        "description": "Canal dedicado al análisis profundo de la cultura, el cine y la sociedad, buscando siempre un criterio propio y fundamentado.",
        "website_promo": "https://masitaprex.com/PeliPREX",
        "order": 2
    },
    "CHANNEL_NAME_3": {
        "id": os.getenv("ID_CANAL_3", "UC_EL_PENSAMIENTO_ID"),
        "topics": [
            "Reflexiones sobre la vida",
            "Psicología aplicada",
            "Grandes misterios de la mente",
            "Sabiduría ancestral",
            "Crecimiento espiritual"
        ],
        "description": "Canal dedicado a explorar las profundidades del pensamiento humano, la psicología y la sabiduría que trasciende el tiempo.",
        "website_promo": "https://masitaprex.com/PeliPREX",
        "order": 3
    }
}

def get_channel_config(channel_name):
    return CHANNEL_CONFIGS.get(channel_name)

def get_all_channels_ordered():
    return sorted(CHANNEL_CONFIGS.items(), key=lambda x: x[1]['order'])
