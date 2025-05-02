from typing import Tuple

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
        respuesta = obtener_mensaje_presentacion()
        respuesta["estado"] = "consentimiento"
        return respuesta, datos_guardados

    # --- Consentimiento ---
    if estado_actual == "consentimiento":
        texto_limpio = limpiar_texto(texto_usuario)
        intencion = detectar_intencion(texto_limpio)
        if intencion == "afirmativo":
            respuesta = obtener_mensaje_nombre()
            respuesta["estado"] = "preguntar_nombre"
        elif intencion == "negativo":
            respuesta = {
                "estado": FIN,
                "mensaje": "Entiendo tu decisión. Gracias por tu tiempo. Si en otro momento quieres hablar, estaré disponible.",
                "modo_entrada": "fin",
                "sugerencias": []
            }
        else:
            respuesta = obtener_mensaje_presentacion()
            respuesta["estado"] = "consentimiento"
        return respuesta, datos_guardados

    # --- Preguntar nombre ---
    if estado_actual == "preguntar_nombre":
        nombre_usuario = extraer_nombre(texto_usuario)
        datos_guardados["nombre_usuario"] = nombre_usuario
        registrar_interaccion(session_id, estado_actual,
                              "¿Con qué nombre o seudónimo puedo dirigirme a ti?", texto_usuario)

        respuesta = obtener_mensaje_identidad(nombre_usuario)
        respuesta["estado"] = "preguntar_identidad"
        return respuesta, datos_guardados

    # --- Preguntar identidad ---
    if estado_actual == "preguntar_identidad":
        from core.empathy_utils import detectar_ambiguedad_identidad

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
        respuesta = obtener_mensaje_exploracion_tristeza(nombre)
        respuesta["estado"] = "inicio_exploracion_tristeza"
        return respuesta, datos_guardados


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
            respuesta = obtener_mensaje_frecuencia_tristeza()
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

        respuesta = obtener_mensaje_duracion_tristeza()
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

        respuesta = obtener_mensaje_intensidad_tristeza()
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

        # Generar resumen de evaluación (media)
        resumen = generar_resumen_evaluacion(session_id)
        datos_guardados["resumen"] = resumen

        media = resumen["perfil_emocional"].get("media", 0)
        perfil = resumen["evaluacion"].capitalize()

        # Mensaje personalizado por perfil
        if resumen["evaluacion"] == "leve":
            mensaje_extra = (
                "Tu nivel actual de tristeza parece ser bajo o puntual. Esto indica que, en general, estás gestionando tus emociones de forma saludable.\n\n"
                "Mantén esos hábitos positivos que te ayudan a mantener el equilibrio emocional, y no dudes en darte espacio para sentir y reflexionar cuando lo necesites."
            )
        elif resumen["evaluacion"] == "moderado":
            mensaje_extra = (
                "Tu nivel de tristeza es moderado. Es normal atravesar etapas así, y lo importante es que estás prestando atención a tu bienestar.\n\n"
                "Considera dedicar tiempo a actividades que te aporten calma, rodearte de personas de confianza y, si lo necesitas, expresar lo que sientes sin juzgarte.\n"
                "Reconocer tus emociones es un paso valiente hacia el cuidado personal."
            )
        else:
            mensaje_extra = (
                "Tu nivel de tristeza actual es alto, lo cual puede estar generando un malestar significativo en tu día a día.\n\n"
                "Recuerda que no estás solo/a: hablar con un profesional puede ayudarte a entender mejor lo que estás atravesando y darte herramientas para afrontarlo.\n"
                "Buscar apoyo no es signo de debilidad, sino un acto de fortaleza y autocuidado. Tu bienestar es importante."
            )

        mensaje = (
            f"🔍 **Resumen de evaluación emocional:**\n"
            f"- Perfil detectado: {perfil}\n"
            f"- Puntuación emocional media: {media}/10\n\n"
            f"{mensaje_extra}\n\n"
            "¿Te gustaría valorar cómo te has sentido conversando conmigo? (0 = nada empático, 10 = muy empático)"
        )

        respuesta = {
            "estado": "preguntar_empatia",
            "mensaje": mensaje,
            "modo_entrada": "numero",
            "sugerencias": []
        }
        return respuesta, datos_guardados

    # --- Mostrar resumen de evaluación ---
    if estado_actual == "mostrar_resumen":
        resumen = generar_resumen_evaluacion(session_id)
        datos_guardados["resumen"] = resumen

        mensaje = (
            f"🔍 **Resumen de evaluación emocional:**\n"
            f"- Perfil detectado: {resumen['evaluacion'].capitalize()}\n"
            f"- Puntuación acumulada: {resumen['perfil_emocional'].get('total', 0)}\n\n"
            "¿Te gustaría valorar cómo te has sentido conversando conmigo? (0 = nada empático, 10 = muy empático)"
        )

        respuesta = {
            "estado": "preguntar_empatia",
            "mensaje": mensaje,
            "modo_entrada": "numero",
            "sugerencias": []
        }
        return respuesta, datos_guardados

    # --- Preguntar valoración de empatía ---
    if estado_actual == "preguntar_empatia":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        coincidencias = re.findall(r"\b([0-9]|10)\b", texto_limpio)
        if coincidencias:
            try:
                empatia = int(coincidencias[0])
                empatia = max(0, min(empatia, 10))
            except ValueError:
                empatia = 5
        else:
            # En caso de ambigüedad no numérica
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        datos_guardados["valoracion_empatia"] = empatia

        resumen = datos_guardados.get("resumen", {})
        riesgo = resumen.get("evaluacion") == "grave"

        if empatia >= 8:
            mensaje_final = (
                "Me alegra mucho saber que te has sentido acompañado/a durante esta conversación. "
                "Tu bienestar importa, y estoy aquí siempre que necesites hablar. "
                "Gracias por confiar en este espacio."
            )
        elif empatia >= 5:
            mensaje_final = (
                "Gracias por tu valoración. Me esforzaré en seguir mejorando para ofrecerte una experiencia más empática y cercana. "
                "Recuerda que siempre estaré disponible si deseas volver a hablar."
            )
        else:
            mensaje_final = (
                "Lamento que esta experiencia no haya sido tan empática como esperabas. "
                "Tu opinión es valiosa para mejorar este espacio de escucha y apoyo. "
                "Gracias por haber participado con sinceridad."
            )

        if riesgo:
            mensaje_final = (
                "📢 *Detectamos un posible nivel elevado de malestar.*\n"
                "Te recomendamos que hables con un profesional de la salud mental.\n\n" + mensaje_final
            )

        respuesta = {
            "estado": "cierre_final",
            "mensaje": mensaje_final,
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
