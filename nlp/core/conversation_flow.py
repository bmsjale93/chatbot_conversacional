from typing import Tuple

from core import dialog_manager

from core.intent_detector import detectar_intencion
from core.score_manager import (
    asignar_puntuacion,
    obtener_puntuaciones,
    generar_resumen_evaluacion
)
from core.empathy_utils import (
    detectar_ambiguedad,
    generar_respuesta_aclaratoria,
    generar_respuesta_empatica,
    detectar_ambiguedad_identidad
)
from core.database import guardar_interaccion_completa
from core.cleaner import limpiar_texto
from utils.extract_name import extraer_nombre
import re


# Constantes de estado
FIN = "fin"
ERROR = "error"


def registrar_interaccion(session_id: str, estado: str, pregunta: str, respuesta_usuario: str) -> None:
    guardar_interaccion_completa(
        session_id=session_id,
        estado=estado,
        pregunta=pregunta,
        respuesta_usuario=respuesta_usuario
    )


def procesar_mensaje(session_id: str, texto_usuario: str, estado_actual: str, datos_guardados: dict) -> Tuple[dict, dict]:
    """
    Procesa el mensaje recibido según el estado de conversación actual.

    Args:
        session_id (str): ID único de la conversación.
        texto_usuario (str): Mensaje enviado por el usuario.
        estado_actual (str): Estado actual de la conversación.
        datos_guardados (dict): Información acumulada durante la conversación.

    Returns:
        Tuple[dict, dict]: Respuesta que debe enviar el asistente y datos actualizados.
    """

    # --- Fase de presentación ---
    if estado_actual == "presentacion":
        respuesta = dialog_manager.obtener_mensaje_presentacion()
        respuesta["estado"] = "consentimiento"
        return respuesta, datos_guardados

    # --- Consentimiento ---
    if estado_actual == "consentimiento":
        texto_limpio = limpiar_texto(texto_usuario)
        intencion = detectar_intencion(texto_limpio)
        if intencion == "afirmativo":
            respuesta = dialog_manager.obtener_mensaje_nombre()
            respuesta["estado"] = "preguntar_nombre"
        elif intencion == "negativo":
            respuesta = {
                "estado": FIN,
                "mensaje": "Entiendo tu decisión. Gracias por tu tiempo. Si en otro momento quieres hablar, estaré disponible.",
                "modo_entrada": "fin",
                "sugerencias": []
            }
        else:
            respuesta = dialog_manager.obtener_mensaje_presentacion()
            respuesta["estado"] = "consentimiento"
        return respuesta, datos_guardados

    # --- Preguntar nombre ---
    if estado_actual == "preguntar_nombre":
        nombre_usuario = extraer_nombre(texto_usuario)
        datos_guardados["nombre_usuario"] = nombre_usuario
        registrar_interaccion(session_id, estado_actual,
                              "¿Con qué nombre o seudónimo puedo dirigirme a ti?", texto_usuario)

        respuesta = dialog_manager.obtener_mensaje_identidad(nombre_usuario)
        respuesta["estado"] = "preguntar_identidad"
        return respuesta, datos_guardados

    # --- Preguntar identidad ---
    if estado_actual == "preguntar_identidad":
        texto_limpio = texto_usuario.strip().lower()

        if detectar_ambiguedad_identidad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Mapear respuestas comunes a etiquetas válidas
        MAPEO_IDENTIDAD = {
            "masculino": "masculino",
            "hombre": "masculino",
            "femenino": "femenino",
            "mujer": "femenino",
            "no binario": "no binario",
            "nobinario": "no binario",
            "no-binario": "no binario"
        }

        identidad = MAPEO_IDENTIDAD.get(texto_limpio)

        if identidad is None:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["identidad"] = identidad
        registrar_interaccion(session_id, estado_actual,
                              "¿Qué etiqueta identifica mejor tu identidad?", texto_usuario)

        nombre = datos_guardados.get("nombre_usuario", "")
        respuesta = dialog_manager.obtener_mensaje_exploracion_tristeza(nombre)
        respuesta["estado"] = "inicio_exploracion_tristeza"
        return respuesta, datos_guardados

    # ------- APARTADO TRISTEZA ---------
    # --- Inicio de exploración emocional (tristeza) ---
    if estado_actual == "inicio_exploracion_tristeza":

        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # 2. Clasificar respuesta explícita si es posible
        respuestas_positivas = {
            "sí", "si", "sí últimamente", "sí actualmente", "sí me he sentido triste",
            "me siento triste", "últimamente sí", "sí he estado mal", "sí algo"
        }
        respuestas_negativas = {
            "no", "no últimamente", "no me siento triste", "no ahora", "en general estoy bien",
            "he estado bien", "no no realmente", "no especialmente"
        }

        intencion = None
        for afirmativa in respuestas_positivas:
            if afirmativa in texto_limpio:
                intencion = "afirmativo"
                break
        if not intencion:
            for negativa in respuestas_negativas:
                if negativa in texto_limpio:
                    intencion = "negativo"
                    break

        # 3. Si no hay coincidencia exacta, usar modelo de detección
        if not intencion:
            intencion = detectar_intencion(texto_limpio)

        # 4. Registrar la interacción
        registrar_interaccion(session_id, estado_actual,
                            "¿Has experimentado tristeza recientemente?", texto_usuario)

        # 5. Responder según intención
        if intencion == "afirmativo":
            respuesta = dialog_manager.obtener_mensaje_frecuencia_tristeza()
            respuesta["estado"] = "preguntar_frecuencia"
            respuesta["mensaje"] = generar_respuesta_empatica(
                respuesta["mensaje"], tipo="tristeza")
        elif intencion == "negativo":
            respuesta = {
                "estado": FIN,
                "mensaje": (
                    "¡Me alegra saberlo! Parece que no estás experimentando tristeza en estos momentos. "
                    "Gracias por tu participación."
                ),
                "modo_entrada": "fin",
                "sugerencias": []
            }
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        return respuesta, datos_guardados


    # --- Preguntar frecuencia de tristeza ---
    if estado_actual == "preguntar_frecuencia":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["frecuencia_tristeza"] = texto_usuario
        asignar_puntuacion(session_id, "frecuencia", texto_limpio)
        registrar_interaccion(
            session_id,
            estado_actual,
            "¿Con qué frecuencia sueles experimentar tristeza?",
            texto_usuario
        )

        respuesta = dialog_manager.obtener_mensaje_duracion_tristeza()
        respuesta["estado"] = "preguntar_duracion"
        return respuesta, datos_guardados


    # --- Preguntar duración ---
    if estado_actual == "preguntar_duracion":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["duracion_tristeza"] = texto_usuario
        asignar_puntuacion(session_id, "duracion", texto_limpio)
        registrar_interaccion(session_id, estado_actual,
                            "¿Cuánto tiempo dura generalmente esa tristeza?", texto_usuario)

        respuesta = dialog_manager.obtener_mensaje_intensidad_tristeza()
        respuesta["estado"] = "intensidad_tristeza"
        return respuesta, datos_guardados


    # --- Preguntar intensidad ---
    if estado_actual == "intensidad_tristeza":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["intensidad_tristeza"] = texto_usuario
        asignar_puntuacion(session_id, "intensidad", texto_limpio)
        registrar_interaccion(session_id, estado_actual,
                              "Cuando sientes tristeza, ¿cómo de intensa es?", texto_usuario)

        # Transición directa al siguiente bloque sin mostrar resumen
        respuesta = dialog_manager.obtener_mensaje_anhedonia()
        return respuesta, datos_guardados

    # ------- APARTADO ANHEDONIA ---------
    # --- Preguntar sobre anhedonia ---
    if estado_actual == "preguntar_anhedonia":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        registrar_interaccion(session_id, estado_actual,
                              "¿Has notado pérdida de interés o placer en actividades que antes disfrutabas?", texto_usuario)

        intencion = detectar_intencion(texto_limpio)

        if intencion == "afirmativo":
            datos_guardados["anhedonia"] = True
            respuesta = dialog_manager.obtener_mensaje_anhedonia_profunda()


        elif intencion == "negativo":
            datos_guardados["anhedonia"] = False
            respuesta = {
                "estado": "preguntar_desesperanza",
                "mensaje": (
                    "Me alegra saber que sigues disfrutando de tus actividades. Continuemos con la siguiente pregunta."
                ),
                "modo_entrada": "texto_libre",
                "sugerencias": []
            }
            
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        return respuesta, datos_guardados

    # --- Detalle actividades con anhedonia ---
    if estado_actual == "detalle_anhedonia":
        registrar_interaccion(session_id, estado_actual,
                            "¿Qué actividades has dejado de disfrutar?", texto_usuario)

        datos_guardados["actividades_sin_disfrute"] = texto_usuario

        respuesta = dialog_manager.obtener_mensaje_desesperanza()
        return respuesta, datos_guardados


    # --- Preguntar desesperanza ---
    if estado_actual == "preguntar_desesperanza":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        registrar_interaccion(
            session_id, estado_actual,
            "¿Te resulta difícil encontrar algo que te ilusione o motive al pensar en el futuro?",
            texto_usuario
        )

        intencion = detectar_intencion(texto_limpio)

        if intencion == "afirmativo":
            datos_guardados["desesperanza"] = True
            puntuacion = 1
        elif intencion == "negativo":
            datos_guardados["desesperanza"] = False
            puntuacion = 0
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["puntuacion_desesperanza"] = puntuacion

        respuesta = dialog_manager.obtener_mensaje_inutilidad()
        return respuesta, datos_guardados


    # --- Preguntar sentimientos de inutilidad ---
    if estado_actual == "preguntar_inutilidad":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        registrar_interaccion(
            session_id, estado_actual,
            "¿En los últimos días has sentido que no eres suficiente?", texto_usuario
        )

        intencion = detectar_intencion(texto_limpio)

        if intencion == "afirmativo":
            datos_guardados["inutilidad"] = True
            datos_guardados["puntuacion_inutilidad"] = 1

            respuesta = dialog_manager.obtener_detalle_inutilidad()

        elif intencion == "negativo":
            datos_guardados["inutilidad"] = False
            datos_guardados["puntuacion_inutilidad"] = 0

            respuesta = dialog_manager.obtener_mensaje_esperar_siguiente_pregunta()

        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        return respuesta, datos_guardados


    # --- Detalle situaciones de inutilidad ---
    if estado_actual == "detalle_inutilidad":
        registrar_interaccion(session_id, estado_actual,
                            "¿En qué situaciones sientes que no eres suficiente?", texto_usuario)

        datos_guardados["situaciones_inutilidad"] = texto_usuario

        # De momento avanzamos a un estado genérico
        respuesta = dialog_manager.obtener_mensaje_esperar_siguiente_pregunta()
        return respuesta, datos_guardados










    # --- Esperar próxima sección aún no definida ---
    if estado_actual == "esperar_siguiente_pregunta":
        respuesta = {
            "estado": FIN,
            "mensaje": (
                "Gracias por compartir todo esto conmigo. Tus respuestas son muy valiosas.\n\n"
                "De momento, esta es toda la información que necesitaba recopilar. Pronto continuaré con más preguntas."
            ),
            "modo_entrada": "fin",
            "sugerencias": []
        }
        return respuesta, datos_guardados


    # --- Fallback de error ---
    respuesta = {
        "estado": ERROR,
        "mensaje": "Ha ocurrido un error inesperado. Vamos a reiniciar la conversación.",
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }
    return respuesta, datos_guardados
