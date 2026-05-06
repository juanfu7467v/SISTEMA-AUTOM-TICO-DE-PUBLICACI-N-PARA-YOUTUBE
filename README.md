# 📺 Sistema Automático de Análisis para YouTube - El Tío Jota

Este sistema avanzado automatiza la gestión de contenidos para YouTube, integrando análisis de tendencias, inteligencia artificial (OpenAI) y un flujo de trabajo optimizado para despliegue en Fly.io con rotación automática de canales.

## ✨ Novedades y Mejoras Clave

El sistema ha sido actualizado para ser completamente autónomo, eficiente y estable:

*   **Motor de IA Único (OpenAI)**: Se ha eliminado por completo la integración con Gemini AI. Ahora, el sistema utiliza exclusivamente OpenAI para realizar análisis profundos de tendencias y generar recomendaciones estratégicas.
*   **Automatización cada 5 Horas**: El sistema está diseñado para activarse cada 5 horas mediante una petición al endpoint `/start-autonomous-job`.
*   **Flujo de Trabajo Rotativo**: En cada ejecución, el sistema revisa el archivo `data.json` para identificar qué canal fue analizado previamente y continúa automáticamente con el siguiente canal pendiente en la lista configurada.
*   **Gestión de Recursos y Keep-Alive**: 
    *   **Keep-Alive**: Durante la ejecución de procesos pesados, el sistema utiliza un mecanismo interno de `/keep-alive` para evitar que la máquina se suspenda prematuramente.
    *   **Auto-Sleep**: Una vez completado el análisis y enviado el reporte, la máquina se apaga automáticamente (`os._exit(0)`) para ahorrar recursos, quedando lista para la siguiente petición.
*   **Análisis de Tendencias con YouTube Data API**: Utiliza la YouTube Data API para validar temas populares y asegurar que las recomendaciones tengan un alto potencial de visualizaciones.
*   **Envío de Recomendaciones**: Los resultados se envían automáticamente a un servidor externo mediante una petición POST en formato JSON.

## 🚀 Flujo de Trabajo Automatizado

1.  **Activación**: Una petición externa (ej. GitHub Action cada 5 horas) llama al endpoint `/start-autonomous-job`.
2.  **Rotación de Canales**: El sistema determina el siguiente canal a analizar basándose en el historial de `data.json`.
3.  **Análisis y Validación**: Se obtienen tendencias y se validan mediante YouTube Search para asegurar un tráfico potencial > 100k vistas.
4.  **Generación con OpenAI**: Se genera una recomendación detallada (título viral, idea de contenido, formato, etc.).
5.  **Persistencia y Envío**: Se guarda el progreso en `data.json` (enviado a GitHub) y se reporta al servidor de destino.
6.  **Apagado Seguro**: El sistema finaliza su ejecución y libera recursos hasta la próxima llamada.

## ⚙️ Configuración y Despliegue

### Requisitos (Variables de Entorno)

*   `YOUTUBE_API_KEY`: Clave de API de Google Cloud.
*   `OPENAI_API_KEY`: Clave de API de OpenAI (reemplaza a Gemini).
*   `GITHUB_TOKEN` y `GITHUB_REPO`: Para la persistencia del historial en `data.json`.
*   `ID_CANAL`, `ID_CANAL_2`, `ID_CANAL_3`: IDs de los canales configurados.

### Activación Programada (GitHub Actions)

Se recomienda configurar un workflow en `.github/workflows/autonomous_job.yml` con la siguiente estructura:

```yaml
name: Automatización cada 5 horas

on:
  schedule:
    - cron: '0 */5 * * *'
  workflow_dispatch:

jobs:
  activate:
    runs-on: ubuntu-latest
    steps:
      - name: Despertar y Ejecutar Job
        run: |
          curl -X POST https://tu-app-en-fly.fly.dev/start-autonomous-job
```

---
Desarrollado para el canal **El Tío Jota**.
