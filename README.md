# 📺 Sistema Automático de Publicación para YouTube - Canal "El Tío Jota"

Este sistema avanzado automatiza la gestión de contenidos para YouTube, integrando análisis de tendencias, inteligencia artificial y un flujo de trabajo optimizado para despliegue en Fly.io.

## ✨ Novedades y Mejoras Clave

El sistema ha sido significativamente mejorado para un funcionamiento más autónomo y eficiente, enfocado en la detección de tendencias y la generación de recomendaciones:

*   **Análisis de Tendencias con YouTube Data API**: Utiliza los métodos `videoCategories` y `videos.list` (con `chart='mostPopular'`) de la YouTube Data API para identificar las tendencias actuales de YouTube. Esto permite al sistema analizar qué contenido está siendo popular en tiempo real.
*   **Generación de Recomendaciones con Gemini 2.5 Flash**: Se ha integrado el modelo de inteligencia artificial `gemini-2.5-flash` para analizar las tendencias obtenidas y generar recomendaciones estratégicas de contenido. Estas recomendaciones incluyen un tema, título, idea de contenido, formato sugerido, hora óptima de publicación y el canal de destino (`ID_CANAL`, `ID_CANAL_2` o `ID_CANAL_3`).
*   **Envío de Recomendaciones a Servidor Externo**: Las recomendaciones generadas se envían automáticamente a un servidor externo (`https://crear-videos-subir-youtuve.fly.dev/`) mediante una petición POST en formato JSON, reemplazando la comunicación vía Telegram.
*   **Funcionamiento Elástico en Fly.io**: Configurado para un despliegue eficiente en Fly.io, utilizando `auto_stop_machines` para que el servidor se apague automáticamente después de completar su tarea, minimizando el consumo de recursos.
*   **Activación Diaria Autónoma**: El sistema se activa diariamente a las 5:00 AM (UTC) mediante un GitHub Action, que realiza una llamada HTTP al endpoint `/start-autonomous-job` para iniciar el proceso de análisis y generación de recomendaciones.
*   **Multithreading para Eficiencia**: Los procesos de análisis y generación se ejecutan en hilos separados para asegurar una respuesta rápida y un procesamiento eficiente.

## 🚀 Flujo de Trabajo Automatizado

1.  **Activación Diaria**: Un GitHub Action programado llama al endpoint `/start-autonomous-job` del servidor en Fly.io a las 5:00 AM (UTC).
2.  **Análisis de Tendencias**: El sistema utiliza la YouTube Data API para obtener las categorías de video y los videos más populares del momento.
3.  **Generación de Recomendaciones**: Gemini 2.5 Flash analiza los datos de tendencias y genera una recomendación de contenido detallada en formato JSON.
4.  **Envío de Datos**: La recomendación en formato JSON se envía al servidor externo (`https://crear-videos-subir-youtuve.fly.dev/`).
5.  **Apagado Automático**: Una vez completado el proceso, el servidor en Fly.io entra en modo de reposo profundo gracias a la configuración `auto_stop_machines`, consumiendo casi cero recursos hasta la próxima activación.

## ⚙️ Configuración y Despliegue en Fly.io

### Requisitos

Para el correcto funcionamiento del sistema, se requieren las siguientes variables de entorno:

*   `YOUTUBE_API_KEY`: Clave de API de Google Cloud con acceso a YouTube Data API v3.
*   `GEMINI_API_KEY`: Clave de API para Google AI Studio (necesaria para el modelo `gemini-2.5-flash`).
*   `ID_CANAL`: ID del primer canal de YouTube al que se pueden enviar recomendaciones.
*   `ID_CANAL_2`: ID del segundo canal de YouTube al que se pueden enviar recomendaciones.
*   `ID_CANAL_3`: ID del tercer canal de YouTube al que se pueden enviar recomendaciones.

### Despliegue

El sistema está configurado para ser desplegado en Fly.io. El archivo `fly.toml` ya incluye la configuración necesaria para el auto-apagado y el nombre de la aplicación (`sistema-analisis-canales`).

### Activación Diaria con GitHub Actions

Para la activación diaria, **debes crear manualmente** el siguiente archivo en tu repositorio de GitHub en la ruta `.github/workflows/daily_activation.yml`:

```yaml
name: Activación Diaria Sistema YouTube

on:
  schedule:
    # 5:00 AM UTC (Ajusta según tu zona horaria si es necesario)
    - cron: '0 5 * * *'
  workflow_dispatch: # Permite ejecutarlo manualmente para probar

jobs:
  activate:
    runs-on: ubuntu-latest
    steps:
      - name: Llamar al Endpoint de Fly.io
        run: |
          curl -X POST https://sistema-analisis-canales.fly.dev/start-autonomous-job \
          -H "Content-Type: application/json"
```

---
Desarrollado para el canal **El Tío Jota**.
