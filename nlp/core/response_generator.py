# Importamos las funciones necesarias de otros módulos
from core.emotion_model import analizar_sentimiento
from core.moderator import contiene_lenguaje_inapropiado
from core.cache import obtener_cache, guardar_cache
from core.database import guardar_interaccion

# Función principal para generar una respuesta basada en el estado emocional
def generar_respuesta(texto: str) -> dict:
    """
    Genera una respuesta empática basada en el análisis emocional del mensaje.
    Utiliza caché para optimizar y guarda cada interacción en la base de datos.
    Maneja errores internos para asegurar una respuesta válida en todos los casos.
    """
    try:
        # Primero, revisamos si ya existe una respuesta en caché
        respuesta_cacheada = obtener_cache(texto)
        if respuesta_cacheada:
            return respuesta_cacheada

        # Verificamos si el texto contiene lenguaje inapropiado
        if contiene_lenguaje_inapropiado(texto):
            respuesta_generada = {
                "estado_emocional": "alerta",
                "respuesta": "Hemos detectado lenguaje inapropiado. Por favor, cuida tu expresión para que podamos ayudarte mejor."
            }
            guardar_interaccion(
                texto, respuesta_generada["respuesta"], respuesta_generada["estado_emocional"]
            )
            guardar_cache(texto, respuesta_generada)
            return respuesta_generada

        # Analizamos el estado emocional del mensaje
        resultado_emocion = analizar_sentimiento(texto)
        estado = resultado_emocion.get("estado_emocional", "neutral")

        # Generamos una respuesta empática según el estado emocional detectado
        if estado == "negativo":
            respuesta = "Parece que estás pasando por un momento difícil. Estoy aquí para escucharte. ¿Te gustaría contarme más?"
        elif estado == "positivo":
            respuesta = "Me alegra saber que te sientes bien. ¿Quieres compartir más sobre eso?"
        elif estado == "neutral":
            respuesta = "Gracias por compartir cómo te sientes. ¿Quieres contarme algo más?"
        else:
            respuesta = "Gracias por tu mensaje. ¿Te gustaría seguir hablando?"

        respuesta_generada = {
            "estado_emocional": estado,
            "respuesta": respuesta
        }

        guardar_interaccion(
            texto, respuesta_generada["respuesta"], respuesta_generada["estado_emocional"]
        )
        guardar_cache(texto, respuesta_generada)
        return respuesta_generada

    except Exception as e:
        # Manejo de errores inesperados para evitar caídas del NLP
        return {
            "estado_emocional": "error",
            "respuesta": f"❌ Error interno: {str(e)}"
        }
