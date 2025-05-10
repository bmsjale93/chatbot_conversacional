from core.emotion_model import analizar_sentimiento
from core.moderator import contiene_lenguaje_inapropiado
from core.cache import obtener_cache, guardar_cache
from core.database import guardar_interaccion


def generar_respuesta_emocional(estado: str) -> str:
    """Genera una respuesta empática basada en el estado emocional."""
    respuestas = {
        "negativo": "Parece que estás pasando por un momento difícil. Estoy aquí para escucharte. ¿Te gustaría contarme más?",
        "positivo": "Me alegra saber que te sientes bien. ¿Quieres compartir más sobre eso?",
        "neutral": "Gracias por compartir cómo te sientes. ¿Quieres contarme algo más?",
    }
    return respuestas.get(estado, "Gracias por tu mensaje. ¿Te gustaría seguir hablando?")


def procesar_texto(texto: str) -> dict:
    """Analiza el texto, verifica lenguaje y genera una respuesta."""
    if contiene_lenguaje_inapropiado(texto):
        return {
            "estado_emocional": "alerta",
            "respuesta": "Hemos detectado lenguaje inapropiado. Por favor, cuida tu expresión para que podamos ayudarte mejor."
        }

    resultado_emocion = analizar_sentimiento(texto)
    estado = resultado_emocion.get("estado_emocional", "neutral").lower()

    return {
        "estado_emocional": estado,
        "respuesta": generar_respuesta_emocional(estado)
    }


def generar_respuesta(texto: str) -> dict:
    """Genera una respuesta empática usando caché y guardado de historial."""
    try:
        if (respuesta := obtener_cache(texto)):
            return respuesta

        respuesta_generada = procesar_texto(texto)

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
            "respuesta": f"Error interno inesperado: {str(e)}"
        }
