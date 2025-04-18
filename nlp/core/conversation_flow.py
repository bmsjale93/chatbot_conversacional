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
from core.score_manager import (
    asignar_puntuacion,
    obtener_puntuaciones,
    generar_resumen_evaluacion
)
from core.empathy_utils import (
    detectar_ambiguedad,
    generar_respuesta_aclaratoria,
    generar_respuesta_empatica
)
from core.database import guardar_interaccion_completa

# Tabla de transiciones
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
    "preguntar_intensidad": "mostrar_resumen",
    "mostrar_resumen": "preguntar_empatia",
    "preguntar_empatia": "cierre_final"
}


def registrar_interaccion(session_id: str, estado: str, pregunta: str, respuesta_usuario: str):
    guardar_interaccion_completa(
        session_id=session_id,
        estado=estado,
        pregunta=pregunta,
        respuesta_usuario=respuesta_usuario
    )


def procesar_mensaje(session_id: str, texto_usuario: str, estado_actual: str, datos_guardados: dict) -> tuple:

    if estado_actual == "presentacion":
        respuesta = obtener_mensaje_presentacion()
        respuesta["estado"] = "consentimiento"
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
        registrar_interaccion(session_id, estado_actual,
                              "¿Con qué nombre o seudónimo puedo dirigirme a ti?", texto_usuario)
        respuesta = obtener_mensaje_identidad(nombre_usuario)
        respuesta["estado"] = "preguntar_identidad"
        return respuesta, datos_guardados

    elif estado_actual == "preguntar_identidad":
        identidad = texto_usuario.strip().lower()
        datos_guardados["identidad"] = identidad
        registrar_interaccion(session_id, estado_actual,
                              "¿Qué etiqueta identifica mejor tu identidad?", texto_usuario)
        nombre = datos_guardados.get("nombre_usuario", "")
        respuesta = obtener_mensaje_exploracion_tristeza(nombre)
        respuesta["estado"] = "inicio_exploracion_tristeza"
        return respuesta, datos_guardados

    elif estado_actual == "inicio_exploracion_tristeza":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        intencion = detectar_intencion(texto_usuario)
        registrar_interaccion(session_id, estado_actual,
                              "¿Has experimentado tristeza recientemente?", texto_usuario)

        if intencion == "afirmativo":
            respuesta = obtener_mensaje_frecuencia_tristeza()
            respuesta["estado"] = "preguntar_frecuencia"
            respuesta["mensaje"] = generar_respuesta_empatica(
                respuesta["mensaje"], "tristeza")
        elif intencion == "negativo":
            respuesta = {
                "estado": "fin",
                "mensaje": (
                    "¡Me alegra saberlo! Parece que no estás experimentando tristeza en estos momentos. "
                    "Gracias por tu participación."
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
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["frecuencia_tristeza"] = texto_usuario
        asignar_puntuacion(session_id, "frecuencia", texto_usuario)
        registrar_interaccion(session_id, estado_actual,
                              "¿Con qué frecuencia sueles experimentar tristeza?", texto_usuario)
        respuesta = obtener_mensaje_duracion_tristeza()
        respuesta["estado"] = "preguntar_duracion"
        return respuesta, datos_guardados

    elif estado_actual == "preguntar_duracion":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["duracion_tristeza"] = texto_usuario
        asignar_puntuacion(session_id, "duracion", texto_usuario)
        registrar_interaccion(session_id, estado_actual,
                              "¿Cuánto tiempo dura generalmente esa tristeza?", texto_usuario)
        respuesta = obtener_mensaje_intensidad_tristeza()
        respuesta["estado"] = "preguntar_intensidad"
        return respuesta, datos_guardados

    elif estado_actual == "preguntar_intensidad":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["intensidad_tristeza"] = texto_usuario
        asignar_puntuacion(session_id, "intensidad", texto_usuario)
        registrar_interaccion(session_id, estado_actual,
                              "Cuando sientes tristeza, ¿cómo de intensa es?", texto_usuario)
        respuesta = {
            "estado": "mostrar_resumen",
            "mensaje": "Gracias por compartir cómo te has sentido. Estoy generando un resumen de tu estado emocional...",
            "modo_entrada": "texto_libre",
            "sugerencias": []
        }
        return respuesta, datos_guardados

    elif estado_actual == "mostrar_resumen":
        resumen = generar_resumen_evaluacion(session_id)
        datos_guardados["resumen"] = resumen

        mensaje = f"""🔍 **Resumen de evaluación emocional:**
- Perfil detectado: {resumen['evaluacion'].capitalize()}
- Puntuación acumulada: {resumen['perfil_emocional'].get('total', 0)}

¿Te gustaría valorar cómo te has sentido conversando conmigo? (0 = nada empático, 10 = muy empático)
"""

        respuesta = {
            "estado": "preguntar_empatia",
            "mensaje": mensaje,
            "modo_entrada": "numero",
            "sugerencias": []
        }
        return respuesta, datos_guardados

    elif estado_actual == "preguntar_empatia":
        try:
            empatia = int(texto_usuario.strip())
            empatia = max(0, min(empatia, 10))
        except:
            empatia = 5  # valor por defecto si el input es inválido

        datos_guardados["valoracion_empatia"] = empatia

        resumen = datos_guardados.get("resumen", {})
        riesgo = resumen.get("evaluacion", "") == "grave"

        mensaje_final = (
            "Gracias por tu participación. "
            "Recuerda que buscar ayuda es un acto de valentía. Estoy aquí para apoyarte."
        )

        if riesgo:
            mensaje_final = (
                "📢 *Detectamos un posible nivel elevado de malestar.*\n"
                "Te recomendamos que hables con un profesional de la salud mental.\n\n"
                + mensaje_final
            )

        respuesta = {
            "estado": "cierre_final",
            "mensaje": mensaje_final,
            "modo_entrada": "fin",
            "sugerencias": []
        }
        return respuesta, datos_guardados

    else:
        respuesta = {
            "estado": "error",
            "mensaje": "Ha ocurrido un error inesperado. Vamos a reiniciar la conversación.",
            "modo_entrada": "texto_libre",
            "sugerencias": []
        }
        return respuesta, datos_guardados
