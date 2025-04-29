from core.emotion_model import analizar_sentimiento
from core.moderator import contiene_lenguaje_inapropiado
from core.cache import obtener_cache, guardar_cache
from core.database import guardar_interaccion


def generar_respuesta_emocional(estado: str) -> str:
    """Devuelve una respuesta empática según el estado emocional detectado."""
    respuestas = {
        "negativo": "Parece que estás pasando por un momento difícil. Estoy aquí para escucharte. ¿Te gustaría contarme más?",
        "positivo": "Me alegra saber que te sientes bien. ¿Quieres compartir más sobre eso?",
        "neutral": "Gracias por compartir cómo te sientes. ¿Quieres contarme algo más?",
    }
    return respuestas.get(estado, "Gracias por tu mensaje. ¿Te gustaría seguir hablando?")


def procesar_texto(texto: str) -> dict:
    """Procesa el texto analizando emoción y generando respuesta empática."""
    # 1. Moderación
    if contiene_lenguaje_inapropiado(texto):
        return {
            "estado_emocional": "alerta",
            "respuesta": "Hemos detectado lenguaje inapropiado. Por favor, cuida tu expresión para que podamos ayudarte mejor."
        }

    # 2. Análisis emocional
    resultado_emocion = analizar_sentimiento(texto)
    estado = resultado_emocion.get("estado_emocional", "neutral").lower()

    # 3. Generar respuesta
    return {
        "estado_emocional": estado,
        "respuesta": generar_respuesta_emocional(estado)
    }


def generar_respuesta(texto: str) -> dict:
    """
    Procesa un mensaje de entrada y genera una respuesta empática.
    Usa caché si está disponible y guarda toda interacción en la base de datos.
    """
    try:
        # Revisión de caché
        if (respuesta := obtener_cache(texto)):
            return respuesta

        # Procesar mensaje
        respuesta_generada = procesar_texto(texto)

        # Guardar y cachear
        guardar_interaccion(
            texto,
            respuesta_generada["respuesta"],
            respuesta_generada["estado_emocional"]
        )
        guardar_cache(texto, respuesta_generada)

        return respuesta_generada

    except Exception as e:
        return {
            "estado_emocional": "error",
            "respuesta": f"❌ Error interno inesperado: {str(e)}"
        }
