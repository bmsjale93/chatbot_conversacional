from core.dialog_manager import (
    obtener_mensaje_presentacion,
    obtener_mensaje_nombre,
    obtener_mensaje_identidad,
    obtener_mensaje_exploracion_tristeza,
    obtener_mensaje_frecuencia_tristeza,
    obtener_mensaje_duracion_tristeza,
    obtener_mensaje_intensidad_tristeza
)
from core.intent_detector import detectar_intencion

# Tabla de transiciones (opcional, a modo de referencia)
TRANSICIONES = {
    "presentacion": "consentimiento",
    "consentimiento": {
        "afirmativo": "preguntar_nombre",
        "negativo": "fin"
    },
    "preguntar_nombre": "preguntar_identidad",
    "preguntar_identidad": "inicio_exploracion_tristeza",
    "inicio_exploracion_tristeza": {
        "afirmativo": "preguntar_frecuencia",
        "negativo": "fin"
    },
    "preguntar_frecuencia": "preguntar_duracion",
    "preguntar_duracion": "preguntar_intensidad",
    "preguntar_intensidad": "fin"
}


def procesar_mensaje(session_id: str, texto_usuario: str, estado_actual: str, datos_guardados: dict) -> tuple:
    """
    Procesa el mensaje del usuario según el estado actual.
    Devuelve (respuesta, datos_guardados_actualizados).
    """

    if estado_actual == "presentacion":
        respuesta = obtener_mensaje_presentacion()
        nuevo_estado = "consentimiento"
        respuesta["estado"] = nuevo_estado
        return respuesta, datos_guardados

    elif estado_actual == "consentimiento":
        intencion = detectar_intencion(texto_usuario)

        if intencion == "afirmativo":
            respuesta = obtener_mensaje_nombre()
            respuesta["estado"] = "preguntar_nombre"
        elif intencion == "negativo":
            respuesta = {
                "estado": "fin",
                "mensaje": (
                    "Entiendo tu decisión. Gracias por tu tiempo. "
                    "Si en otro momento quieres hablar, estaré disponible."
                ),
                "modo_entrada": "fin",
                "sugerencias": []
            }
        else:
            respuesta = obtener_mensaje_presentacion()
            respuesta["estado"] = "consentimiento"

        return respuesta, datos_guardados

    elif estado_actual == "preguntar_nombre":
        nombre_usuario = texto_usuario.strip()
        datos_guardados["nombre_usuario"] = nombre_usuario
        respuesta = obtener_mensaje_identidad(nombre_usuario)
        respuesta["estado"] = "preguntar_identidad"
        return respuesta, datos_guardados

    elif estado_actual == "preguntar_identidad":
        identidad = texto_usuario.strip().lower()
        datos_guardados["identidad"] = identidad
        nombre = datos_guardados.get("nombre_usuario", "")
        respuesta = obtener_mensaje_exploracion_tristeza(nombre)
        respuesta["estado"] = "inicio_exploracion_tristeza"
        return respuesta, datos_guardados

    elif estado_actual == "inicio_exploracion_tristeza":
        intencion = detectar_intencion(texto_usuario)

        if intencion == "afirmativo":
            respuesta = obtener_mensaje_frecuencia_tristeza()
            respuesta["estado"] = "preguntar_frecuencia"
        elif intencion == "negativo":
            respuesta = {
                "estado": "fin",
                "mensaje": (
                    "¡Me alegra saberlo! Parece que no estás experimentando tristeza en estos momentos. "
                    "Gracias por tu participación. 😊"
                ),
                "modo_entrada": "fin",
                "sugerencias": []
            }
        else:
            nombre = datos_guardados.get("nombre_usuario", "")
            respuesta = obtener_mensaje_exploracion_tristeza(nombre)
            respuesta["estado"] = "inicio_exploracion_tristeza"

        return respuesta, datos_guardados

    elif estado_actual == "preguntar_frecuencia":
        datos_guardados["frecuencia_tristeza"] = texto_usuario
        respuesta = obtener_mensaje_duracion_tristeza()
        respuesta["estado"] = "preguntar_duracion"
        return respuesta, datos_guardados

    elif estado_actual == "preguntar_duracion":
        datos_guardados["duracion_tristeza"] = texto_usuario
        respuesta = obtener_mensaje_intensidad_tristeza()
        respuesta["estado"] = "preguntar_intensidad"
        return respuesta, datos_guardados

    elif estado_actual == "preguntar_intensidad":
        datos_guardados["intensidad_tristeza"] = texto_usuario
        respuesta = {
            "estado": "fin",
            "mensaje": (
                "¡Gracias por compartir cómo te has sentido! "
                "Con esta información podremos generar un pequeño informe de tu estado emocional."
            ),
            "modo_entrada": "fin",
            "sugerencias": []
        }
        return respuesta, datos_guardados

    # Fallback de seguridad
    else:
        respuesta = {
            "estado": "error",
            "mensaje": "Ha ocurrido un error inesperado. Vamos a reiniciar la conversación.",
            "modo_entrada": "texto_libre",
            "sugerencias": []
        }
        return respuesta, datos_guardados
