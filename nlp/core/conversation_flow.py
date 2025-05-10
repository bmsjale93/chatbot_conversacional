from typing import Tuple
from core import dialog_manager
from core.emotion_model import analizar_sentimiento
from core.cache import obtener_cache, guardar_cache
from core.intent_detector import detectar_intencion
from core.score_manager import (
    asignar_puntuacion,
    obtener_puntuaciones,
    generar_resumen_evaluacion,
    calcular_puntuacion
)
from core.empathy_utils import (
    detectar_ambiguedad,
    generar_respuesta_aclaratoria,
    generar_respuesta_empatica,
    detectar_ambiguedad_identidad
)
from core.database import guardar_interaccion_completa, generar_pdf_informe
from core.cleaner import limpiar_texto
from utils.extract_name import extraer_nombre
import os
import re

def detectar_emocion(texto_usuario: str) -> str:
    """
    Detecta la emoción principal del texto, usando caché si está disponible.
    """
    cached = obtener_cache(texto_usuario)
    if cached and "estado_emocional" in cached:
        return cached["estado_emocional"]

    resultado = analizar_sentimiento(texto_usuario)
    guardar_cache(texto_usuario, resultado)
    return resultado.get("estado_emocional", "neutral")

# ---------------- Constantes ----------------
FIN = "fin"
ERROR = "error"

# ---------------- Mapeo de estados a funciones ----------------
ESTADOS_DIALOG_MANAGER = {
    "presentacion": dialog_manager.obtener_mensaje_presentacion,
    "consentimiento": dialog_manager.obtener_mensaje_presentacion,
    "preguntar_nombre": dialog_manager.obtener_mensaje_nombre,
    "preguntar_identidad": lambda datos_guardados={}: dialog_manager.obtener_mensaje_identidad(
        datos_guardados.get("nombre_usuario", "")
    ),
    "inicio_exploracion_tristeza": lambda: dialog_manager.obtener_mensaje_exploracion_tristeza(""),
    "preguntar_frecuencia": dialog_manager.obtener_mensaje_frecuencia_tristeza,
    "preguntar_duracion": dialog_manager.obtener_mensaje_duracion_tristeza,
    "intensidad_tristeza": dialog_manager.obtener_mensaje_intensidad_tristeza,
    "preguntar_anhedonia": dialog_manager.obtener_mensaje_anhedonia,
    "detalle_anhedonia": dialog_manager.obtener_mensaje_anhedonia_profunda,
    "preguntar_desesperanza": dialog_manager.obtener_mensaje_desesperanza,
    "preguntar_inutilidad": dialog_manager.obtener_mensaje_inutilidad,
    "detalle_inutilidad": dialog_manager.obtener_detalle_inutilidad,
    "preguntar_ideacion_suicida": dialog_manager.obtener_mensaje_ideacion_suicida,
    "preguntar_fatiga": dialog_manager.obtener_mensaje_fatiga,
    "cerrar_evaluación_por_riesgo_alto": dialog_manager.obtener_cierre_alto_riesgo,
    "preguntar_sueno": dialog_manager.obtener_mensaje_sueno,
    "detalle_sueno": dialog_manager.obtener_detalle_sueno,
    "preguntar_apetito": dialog_manager.obtener_mensaje_apetito,
    "detalle_apetito": dialog_manager.obtener_detalle_apetito,
    "preguntar_concentracion": dialog_manager.obtener_mensaje_concentracion,
    "detalle_concentracion": dialog_manager.obtener_detalle_concentracion,
    "preguntar_agitacion": dialog_manager.obtener_mensaje_agitacion,
    "detalle_agitacion": dialog_manager.obtener_detalle_agitacion,
    "preguntar_antecedentes_generales": dialog_manager.obtener_mensaje_antecedentes_generales,
    "preguntar_consecuentes_generales_1": dialog_manager.obtener_mensaje_consecuentes_generales_1,
    "preguntar_consecuentes_generales_2": dialog_manager.obtener_mensaje_consecuentes_generales_2,
    "preguntar_impacto_diario": dialog_manager.obtener_mensaje_impacto_diario,
    "detalle_impacto_diario": dialog_manager.obtener_detalle_impacto_diario,
    "preguntar_estrategias_1": dialog_manager.obtener_mensaje_estrategias_1,
    "preguntar_estrategias_2": dialog_manager.obtener_mensaje_estrategias_2,
    "cierre_conversacion": dialog_manager.obtener_mensaje_cierre,
    "esperar_siguiente_pregunta": dialog_manager.obtener_mensaje_esperar_siguiente_pregunta,
}



def procesar_mensaje(session_id: str, texto_usuario: str, estado_actual: str, datos_guardados: dict) -> Tuple[dict, dict]:
    # Validación de mensaje vacío
    if not texto_usuario or not texto_usuario.strip():
        respuesta_base_fn = ESTADOS_DIALOG_MANAGER.get(estado_actual)
        if respuesta_base_fn:
            try:
                base = respuesta_base_fn(datos_guardados)
            except TypeError:
                base = respuesta_base_fn()
            return {
                "estado": estado_actual,
                "mensaje": "Por favor, selecciona una opción o escribe algo antes de continuar.",
                "modo_entrada": base.get("modo_entrada", "texto_libre"),
                "sugerencias": base.get("sugerencias", [])
            }, datos_guardados

        return {
            "estado": estado_actual,
            "mensaje": "Por favor, escribe algo antes de continuar.",
            "modo_entrada": "mixto",
            "sugerencias": []
        }, datos_guardados

    # Fase de presentación
    if estado_actual == "presentacion":
        respuesta = dialog_manager.obtener_mensaje_presentacion()
        respuesta["estado"] = "consentimiento"
        return respuesta, datos_guardados

    # Fase de consentimiento
    if estado_actual == "consentimiento":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria("consentimiento"), datos_guardados

        respuestas_negativas_explicitamente = [
            "no", "no quiero continuar", "no, prefiero no continuar",
            "prefiero no continuar", "no deseo continuar"
        ]
        if texto_usuario.strip().lower() in respuestas_negativas_explicitamente:
            respuesta = dialog_manager.obtener_mensaje_consentimiento_rechazado()
            return respuesta, datos_guardados

        intencion = detectar_intencion(texto_usuario)

        if intencion == "afirmativo":
            datos_guardados["consentimiento_aceptado"] = True
            guardar_interaccion_completa(
                session_id=session_id,
                estado=estado_actual,
                pregunta="¿Estás de acuerdo en continuar con esta evaluación emocional?",
                respuesta_usuario=texto_usuario
            )
            respuesta = dialog_manager.obtener_mensaje_nombre()
            respuesta["estado"] = "preguntar_nombre"

        elif intencion == "negativo":
            respuesta = dialog_manager.obtener_mensaje_consentimiento_rechazado()

        else:
            respuesta = dialog_manager.obtener_mensaje_presentacion()
            respuesta["estado"] = "consentimiento"

        return respuesta, datos_guardados

    # Fase de nombre
    if estado_actual == "preguntar_nombre":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        nombre_usuario = extraer_nombre(texto_usuario)
        datos_guardados["nombre_usuario"] = nombre_usuario

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Con qué nombre o seudónimo puedo dirigirme a ti?",
            respuesta_usuario=nombre_usuario
        )

        respuesta = dialog_manager.obtener_mensaje_identidad(nombre_usuario)
        respuesta["estado"] = "preguntar_identidad"
        return respuesta, datos_guardados

    # --- Preguntar identidad ---
    if estado_actual == "preguntar_identidad":
        texto_limpio = texto_usuario.strip().lower()

        # Detectar ambigüedad general o ambigüedad específica de identidad
        if detectar_ambiguedad(texto_limpio) or detectar_ambiguedad_identidad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Mapeo de respuestas comunes a etiquetas estandarizadas
        MAPEO_IDENTIDAD = {
            "masculino": "masculino",
            "hombre": "masculino",
            "femenino": "femenino",
            "mujer": "femenino",
            "no binario": "no binario",
            "nobinario": "no binario",
            "no-binario": "no binario"
        }

        identidad = MAPEO_IDENTIDAD.get(texto_limpio, texto_limpio)  # Usar tal cual si no está mapeada

        # Guardamos ambas versiones
        datos_guardados["identidad"] = identidad
        datos_guardados["identidad_original"] = texto_usuario

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Qué etiqueta identifica mejor tu identidad?",
            respuesta_usuario=texto_usuario
        )

        nombre = datos_guardados.get("nombre_usuario", "")
        respuesta = dialog_manager.obtener_mensaje_exploracion_tristeza(nombre)
        respuesta["estado"] = "inicio_exploracion_tristeza"
        return respuesta, datos_guardados


    # ------------ APARTADO TRISTEZA -------------------
    # --- Inicio de exploración emocional (tristeza) ---
    if estado_actual == "inicio_exploracion_tristeza":
        texto_limpio = limpiar_texto(texto_usuario)

        # Detectar ambigüedad general o ambigüedad específica de identidad
        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Detectar intención (afirmativa, negativa, desconocida)
        intencion = detectar_intencion(texto_limpio)

        # Si la intención es desconocida, comprobar si la respuesta es ambigua
        if intencion == "desconocido":
            if detectar_ambiguedad(texto_limpio):
                return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Detectar emoción SOLO si la intención es afirmativa
        if intencion == "afirmativo":
            resultado_emocional = analizar_sentimiento(texto_usuario)
            emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
            confianza_emocion = resultado_emocional.get("confianza", "0%")
        else:
            emocion_detectada = "neutral"
            confianza_emocion = "100%"

        # Asignar puntuación según intención
        if intencion == "afirmativo":
            puntuacion = 1
        elif intencion == "negativo":
            puntuacion = 0
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Guardar puntuación y emoción
        datos_guardados["respuesta_tristeza"] = texto_usuario
        datos_guardados["emocion_tristeza"] = emocion_detectada
        datos_guardados["puntuacion_tristeza"] = puntuacion

        asignar_puntuacion(session_id, "tristeza", str(puntuacion))

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has experimentado tristeza recientemente?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        # --- Construir respuesta según la intención detectada ---
        if intencion == "afirmativo":
            respuesta_base = dialog_manager.obtener_mensaje_frecuencia_tristeza()
            respuesta = {
                "estado": "preguntar_frecuencia",
                "mensaje": generar_respuesta_empatica(respuesta_base["mensaje"], tipo="tristeza"),
                "modo_entrada": respuesta_base.get("modo_entrada", "texto_libre"),
                "sugerencias": respuesta_base.get("sugerencias", [])
            }

        elif intencion == "negativo":
            respuesta_base = dialog_manager.obtener_mensaje_anhedonia()
            respuesta = {
                "estado": "preguntar_anhedonia",
                "mensaje": respuesta_base["mensaje"],
                "modo_entrada": respuesta_base.get("modo_entrada", "texto_libre"),
                "sugerencias": respuesta_base.get("sugerencias", [])
            }

        return respuesta, datos_guardados


    # --- Preguntar frecuencia de tristeza ---
    if estado_actual == "preguntar_frecuencia":
        texto_limpio = limpiar_texto(texto_usuario)

        # Lista oficial de sugerencias permitidas
        OPCIONES_FRECUENCIA_VALIDAS = {
            limpiar_texto("Todos los días"),
            limpiar_texto("Casi todos los días"),
            limpiar_texto("Muy seguido"),
            limpiar_texto("A menudo"),
            limpiar_texto("Algunas veces por semana"),
            limpiar_texto("De vez en cuando"),
            limpiar_texto("Con poca frecuencia"),
            limpiar_texto("Pocas veces"),
            limpiar_texto("Casi nunca"),
            limpiar_texto("Nunca")
        }

        if texto_limpio not in OPCIONES_FRECUENCIA_VALIDAS:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Detectar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()

        # Guardar información y puntuación
        datos_guardados["frecuencia_tristeza"] = texto_usuario
        datos_guardados["emocion_frecuencia"] = emocion_detectada
        puntuacion_frecuencia = calcular_puntuacion("frecuencia", texto_usuario)
        asignar_puntuacion(session_id, "frecuencia", texto_usuario)

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Con qué frecuencia sueles experimentar tristeza?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion_frecuencia
        )

        respuesta_base = dialog_manager.obtener_mensaje_duracion_tristeza()
        respuesta = {
            "estado": "preguntar_duracion",
            "mensaje": respuesta_base["mensaje"],
            "modo_entrada": respuesta_base.get("modo_entrada", "texto_libre"),
            "sugerencias": respuesta_base.get("sugerencias", [])
        }

        return respuesta, datos_guardados

    # --- Preguntar duración de tristeza ---
    if estado_actual == "preguntar_duracion":
        texto_limpio = limpiar_texto(texto_usuario)

        # Lista oficial de sugerencias permitidas
        OPCIONES_DURACION_VALIDAS = {
            limpiar_texto("Momentos puntuales"),
            limpiar_texto("Unas horas"),
            limpiar_texto("Más de 6 horas"),
            limpiar_texto("Un día o más"),
            limpiar_texto("Entre tres y cinco días"),
            limpiar_texto("Una semana"),
            limpiar_texto("Poco más de una semana"),
            limpiar_texto("Dos semanas"),
            limpiar_texto("Varias semanas"),
            limpiar_texto("Un mes o más")
        }

        if texto_limpio not in OPCIONES_DURACION_VALIDAS:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Detectar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()

        # Guardar info y puntuación
        datos_guardados["duracion_tristeza"] = texto_usuario
        datos_guardados["emocion_duracion"] = emocion_detectada

        puntuacion_duracion = calcular_puntuacion("duracion", texto_usuario)
        asignar_puntuacion(session_id, "duracion", texto_usuario)

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Cuánto tiempo dura generalmente esa tristeza?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion_duracion
        )

        respuesta_base = dialog_manager.obtener_mensaje_intensidad_tristeza()
        respuesta = {
            "estado": "intensidad_tristeza",
            "mensaje": respuesta_base["mensaje"],
            "modo_entrada": respuesta_base.get("modo_entrada", "texto_libre"),
            "sugerencias": respuesta_base.get("sugerencias", [])
        }

        return respuesta, datos_guardados


    # --- Preguntar intensidad ---
    if estado_actual == "intensidad_tristeza":
        texto_limpio = limpiar_texto(texto_usuario)

        # Lista oficial permitida
        OPCIONES_INTENSIDAD_VALIDAS = {str(i) for i in range(1, 11)}

        if texto_limpio not in OPCIONES_INTENSIDAD_VALIDAS:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Detectar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()

        # Guardar puntuación y respuesta
        datos_guardados["intensidad_tristeza"] = texto_usuario
        datos_guardados["emocion_intensidad"] = emocion_detectada

        puntuacion_intensidad = calcular_puntuacion("intensidad", texto_usuario)
        asignar_puntuacion(session_id, "intensidad", texto_usuario)

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="Cuando sientes tristeza, ¿cómo de intensa es?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion_intensidad
        )

        # Transición directa al siguiente bloque
        respuesta = dialog_manager.obtener_mensaje_anhedonia()
        return respuesta, datos_guardados


    # --- APARTADO ANHEDONIA ---
    if estado_actual == "preguntar_anhedonia":
        texto_limpio = texto_usuario.strip()

        # Mapas explícitos de sugerencias
        respuestas_afirmativas = {"Sí, he perdido interés"}
        respuestas_negativas = {"No, sigo disfrutando igual"}

        if texto_limpio in respuestas_afirmativas:
            intencion = "afirmativo"
        elif texto_limpio in respuestas_negativas:
            intencion = "negativo"
        elif detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados
        else:
            intencion = detectar_intencion(texto_usuario)

        # Detectar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza_emocion = resultado_emocional.get("confianza", "0%")

        if intencion == "afirmativo":
            puntuacion = 1
            datos_guardados["anhedonia"] = True
            datos_guardados["emocion_anhedonia"] = emocion_detectada
            datos_guardados["puntuacion_anhedonia"] = puntuacion

            asignar_puntuacion(session_id, "anhedonia", str(puntuacion))

            respuesta_base = dialog_manager.obtener_mensaje_anhedonia_profunda()
            mensaje_empatico = generar_respuesta_empatica(respuesta_base["mensaje"], tipo="anhedonia")

            respuesta = {
                "estado": "detalle_anhedonia",
                "mensaje": mensaje_empatico,
                "modo_entrada": respuesta_base.get("modo_entrada", "mixto"),
                "sugerencias": respuesta_base.get("sugerencias", [])
            }


        elif intencion == "negativo":
            puntuacion = 0
            datos_guardados["anhedonia"] = False
            datos_guardados["emocion_anhedonia"] = emocion_detectada
            datos_guardados["puntuacion_anhedonia"] = puntuacion

            asignar_puntuacion(session_id, "anhedonia", str(puntuacion))

            mensaje_base = (
                "Me alegra saber que sigues disfrutando de tus actividades."
            )
            mensaje_empatico = generar_respuesta_empatica(mensaje_base, tipo=emocion_detectada)

            # Obtenemos la siguiente pregunta
            siguiente = dialog_manager.obtener_mensaje_desesperanza()

            respuesta = {
                "estado": siguiente["estado"],
                "mensaje": f"{mensaje_empatico}\n\n{siguiente['mensaje']}",
                "modo_entrada": siguiente.get("modo_entrada", "mixto"),
                "sugerencias": siguiente.get("sugerencias", [])
            }

        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has notado pérdida de interés o placer en actividades que antes disfrutabas?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        return respuesta, datos_guardados


    # --- Detalle actividades con anhedonia ---
    if estado_actual == "detalle_anhedonia":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza_emocion = resultado_emocional.get("confianza", "0%")

        # Mensaje fijo profesional, sin modificación por emoción
        mensaje_base = (
            "Gracias por compartirlo. A veces, perder interés por lo que antes disfrutábamos puede ser confuso, "
            "desconcertante o incluso doloroso. Reconocerlo ya es un paso importante para comprender cómo te sientes."
        )

        respuesta_base = dialog_manager.obtener_mensaje_desesperanza()
        mensaje_completo = f"{mensaje_base}\n\n{respuesta_base['mensaje']}"

        # Guardar interacción incluyendo la emoción detectada
        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Qué actividades has dejado de disfrutar?",
            respuesta_usuario=texto_usuario,
            emocion=emocion_detectada,
            confianza=confianza_emocion
        )

        # Guardar en memoria temporal
        datos_guardados["actividades_sin_disfrute"] = texto_usuario
        datos_guardados["emocion_ultima_respuesta"] = emocion_detectada
        datos_guardados["confianza_emocion"] = confianza_emocion

        respuesta = {
            "estado": "preguntar_desesperanza",
            "mensaje": mensaje_completo,
            "modo_entrada": respuesta_base.get("modo_entrada", "mixto"),
            "sugerencias": respuesta_base.get("sugerencias", [])
        }

        return respuesta, datos_guardados


    # --- Preguntar desesperanza ---
    if estado_actual == "preguntar_desesperanza":

        # Evaluar ambigüedad sobre el texto original
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        texto_limpio = limpiar_texto(texto_usuario)

        # Detectar intención y emoción
        intencion = detectar_intencion(texto_limpio)
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza_emocion = resultado_emocional.get("confianza", "0%")

        if intencion == "afirmativo":
            datos_guardados["desesperanza"] = True
            puntuacion = 1
            asignar_puntuacion(session_id, "desesperanza", "1")
        elif intencion == "negativo":
            datos_guardados["desesperanza"] = False
            puntuacion = 0
            asignar_puntuacion(session_id, "desesperanza", "0")
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Guardar en memoria
        datos_guardados["puntuacion_desesperanza"] = puntuacion
        datos_guardados["emocion_desesperanza"] = emocion_detectada
        datos_guardados["confianza_emocion_desesperanza"] = confianza_emocion

        # Guardar en base de datos
        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Te resulta difícil encontrar algo que te ilusione o motive al pensar en el futuro?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        # Obtener mensaje siguiente
        siguiente = dialog_manager.obtener_mensaje_inutilidad()

        if intencion == "afirmativo":
            mensaje_intro = generar_respuesta_empatica("", tipo="desesperanza")
        else:
            mensaje_intro = (
                "Me alegra saber que ahora mismo te sientes motivado/a o con metas. "
                "Es importante reconocer esos momentos de estabilidad emocional."
            )

        respuesta = {
            "estado": siguiente["estado"],
            "mensaje": f"{mensaje_intro}\n\n{siguiente['mensaje']}",
            "modo_entrada": siguiente.get("modo_entrada", "mixto"),
            "sugerencias": siguiente.get("sugerencias", [])
        }

        return respuesta, datos_guardados


    if estado_actual == "preguntar_inutilidad":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        intencion = detectar_intencion(texto_limpio)
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza_emocion = resultado_emocional.get("confianza", "0%")

        datos_guardados["emocion_inutilidad"] = emocion_detectada
        datos_guardados["confianza_emocion_inutilidad"] = confianza_emocion

        if intencion == "afirmativo":
            puntuacion = 1
            datos_guardados["inutilidad"] = True
            datos_guardados["puntuacion_inutilidad"] = puntuacion
            asignar_puntuacion(session_id, "inutilidad", str(puntuacion))
            mensaje_intro = generar_respuesta_empatica("", tipo="inutilidad")
            siguiente = dialog_manager.obtener_detalle_inutilidad()

        elif intencion == "negativo":
            puntuacion = 0
            datos_guardados["inutilidad"] = False
            datos_guardados["puntuacion_inutilidad"] = puntuacion
            asignar_puntuacion(session_id, "inutilidad", str(puntuacion))
            mensaje_intro = (
                "Es bueno saber que no has sentido esa carga últimamente. "
                "Reconocer esos momentos de estabilidad es muy valioso."
            )
            siguiente = dialog_manager.obtener_mensaje_ideacion_suicida()

        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿En los últimos días has sentido que no eres suficiente?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion  # Ya garantizado que existe
        )

        respuesta = {
            "estado": siguiente["estado"],
            "mensaje": f"{mensaje_intro}\n\n{siguiente['mensaje']}",
            "modo_entrada": siguiente.get("modo_entrada", "mixto"),
            "sugerencias": siguiente.get("sugerencias", [])
        }

        return respuesta, datos_guardados


    # --- Preguntar ideación suicida ---
    if estado_actual == "preguntar_ideacion_suicida":
        # Mapa exacto de respuestas válidas
        mapa_respuestas = {
            "No, en ningún momento": 0,
            "Sí, pero sin intención de hacerme daño": 1,
            "Sí, pensé en hacerme daño, pero no tengo intención": 2,
            "Sí, pensé en hacerme daño y tengo un plan": 3,
            "No entiendo la pregunta": None  # Se usa para activar aclaración
        }

        if texto_usuario not in mapa_respuestas:
            return {
                "estado": estado_actual,
                "mensaje": (
                    "Parece que tu respuesta no coincide con las opciones disponibles.\n\n"
                    "Por favor, selecciona una de las respuestas propuestas para continuar."
                ),
                "modo_entrada": "sugerencias",
                "sugerencias": list(mapa_respuestas.keys())
            }, datos_guardados

        if texto_usuario == "No entiendo la pregunta":
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Obtener puntuación directamente
        puntuacion = mapa_respuestas[texto_usuario]

        # Analizar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza_emocion = resultado_emocional.get("confianza", "0%")

        # Mensaje según puntuación
        if puntuacion == 0:
            mensaje_ideacion = (
                "Gracias por tu respuesta. Me alegra saber que no has tenido pensamientos de ese tipo últimamente.\n\n"
                "Es importante reconocer estos momentos en los que nos sentimos emocionalmente estables."
            )
        elif puntuacion == 1:
            mensaje_ideacion = (
                "Gracias por compartir algo tan delicado. No estás solo/a en sentirte así en ciertos momentos.\n\n"
                "Reconocer estos pensamientos, incluso sin intención, ya es un paso importante para cuidar tu salud emocional."
            )
        elif puntuacion == 2:
            mensaje_ideacion = (
                "Gracias por tu sinceridad. Entiendo que compartir esto no es fácil.\n\n"
                "Si en algún momento estos pensamientos se vuelven más intensos o difíciles de manejar, por favor considera hablar con un profesional de salud mental.\n"
                "Tu bienestar es muy importante. Seguimos adelante sin presión."
            )
        elif puntuacion == 3:
            mensaje_ideacion = (
                "Gracias por compartirlo. Lamento mucho que sea así, imagino que estás pasando por una situación difícil.\n\n"
                "Lo más adecuado es que contactes ahora mismo con profesionales humanos. Por favor, ponte en contacto con las personas que pueden ayudarte:\n\n"
                "- 📞 024 (Atención al suicidio - Cruz Roja)\n"
                "- 📞 717 00 37 17 (Teléfono de la esperanza)\n"
                "- 📞 112 (Emergencias)"
            )
            mensaje_cierre = dialog_manager.obtener_cierre_alto_riesgo()
            return mensaje_cierre, datos_guardados

        # Guardar datos
        datos_guardados["puntuacion_ideacion_suicida"] = puntuacion
        datos_guardados["ideacion_suicida_texto"] = texto_usuario
        datos_guardados["emocion_ideacion_suicida"] = emocion_detectada
        datos_guardados["confianza_emocion_ideacion"] = confianza_emocion

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has tenido pensamientos relacionados con el suicidio en las últimas dos semanas?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        # Pasar automáticamente a la siguiente pregunta (fatiga)
        siguiente = dialog_manager.obtener_mensaje_fatiga()
        return {
            "estado": siguiente["estado"],
            "mensaje": f"{mensaje_ideacion}\n\n{''.join(siguiente['mensaje'])}",
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Preguntar fatiga ---
    if estado_actual == "preguntar_fatiga":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Detectar intención
        intencion = detectar_intencion(texto_usuario)

        if intencion == "afirmativo":
            puntuacion = 1
            mensaje_empatico = (
                "Gracias por contármelo. Sentirse con menos energía es algo que muchas personas experimentan en momentos difíciles."
            )
        elif intencion == "negativo":
            puntuacion = 0
            mensaje_empatico = (
                "Entiendo, es una buena señal que mantengas tu nivel de energía habitual."
            )
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Analizar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        # Guardar datos
        datos_guardados["puntuacion_fatiga"] = puntuacion
        datos_guardados["fatiga_texto"] = texto_usuario
        datos_guardados["emocion_fatiga"] = emocion
        datos_guardados["confianza_emocion_fatiga"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has notado últimamente que te falta energía o te cansas con más facilidad de lo habitual?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        # Avanzar directamente a la siguiente pregunta: sueño
        siguiente = dialog_manager.obtener_mensaje_sueno()
        return {
            "estado": siguiente["estado"],
            "mensaje": f"{mensaje_empatico}\n\n{''.join(siguiente['mensaje'])}",
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Preguntar sueño ---
    if estado_actual == "preguntar_sueno":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        texto_limpio = texto_usuario.strip().lower()
        mapa_respuestas = {
            "sí, he notado cambios": 1,
            "si, he notado cambios": 1,
            "no, duermo bien": 0,
            "no estoy seguro": None
        }

        # Intento 1: coincidencia exacta
        puntuacion = mapa_respuestas.get(texto_limpio)

        # Intento 2: inferencia por intención
        if puntuacion is None and texto_limpio not in mapa_respuestas:
            intencion = detectar_intencion(texto_usuario)
            if intencion == "afirmativo":
                puntuacion = 1
            elif intencion == "negativo":
                puntuacion = 0
            else:
                return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["puntuacion_sueno"] = puntuacion
        datos_guardados["sueno_texto"] = texto_usuario
        datos_guardados["emocion_sueno"] = emocion
        datos_guardados["confianza_emocion_sueno"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has notado últimamente cambios o dificultades con tu sueño?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        if puntuacion == 1:
            siguiente = dialog_manager.obtener_detalle_sueno()
            mensaje = (
                "Gracias por compartirlo. Los cambios en el sueño pueden tener un gran impacto en cómo nos sentimos durante el día.\n\n"
                f"{siguiente['mensaje']}"
            )
            return {
                "estado": siguiente["estado"],
                "mensaje": mensaje,
                "modo_entrada": siguiente["modo_entrada"],
                "sugerencias": siguiente.get("sugerencias", [])
            }, datos_guardados

        elif puntuacion == 0:
            siguiente = dialog_manager.obtener_mensaje_apetito()
            mensaje = (
                "Me alegra saber que estás durmiendo bien. Un buen descanso es esencial para el bienestar emocional.\n\n"
                "Ahora, vamos a hablar un momento sobre tu apetito.\n\n"
                f"{siguiente['mensaje']}"
            )
            return {
                "estado": siguiente["estado"],
                "mensaje": mensaje,
                "modo_entrada": siguiente["modo_entrada"],
                "sugerencias": siguiente.get("sugerencias", [])
            }, datos_guardados

        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados


    # --- Detalle del sueño ---
    if estado_actual == "detalle_sueno":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["detalle_sueno"] = texto_usuario
        datos_guardados["emocion_detalle_sueno"] = emocion
        datos_guardados["confianza_emocion_detalle_sueno"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Qué tipo de dificultades has notado con tu sueño?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_apetito()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por explicarlo. Comprender cómo afecta el sueño es muy importante.\n\n"
                "Ahora, vamos a hablar un momento sobre tu apetito.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Preguntar Apetito ---
    if estado_actual == "preguntar_apetito":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        texto_limpio = texto_usuario.strip().lower()

        # Mapear solo sugerencias exactas
        mapa_respuestas = {
            "sí, he notado cambios": 1,
            "no, como normal": 0,
            "no estoy seguro": None
        }

        texto_limpio = limpiar_texto(texto_usuario)

        mapa_respuestas_limpio = {limpiar_texto(k): v for k, v in mapa_respuestas.items()}
        puntuacion = mapa_respuestas_limpio.get(texto_limpio)

        # Si no coincide con sugerencias, usar intención
        if puntuacion is None:
            intencion = detectar_intencion(texto_usuario)
            print(f"[DEBUG] Intención detectada: {intencion}")
            if intencion == "afirmativo":
                puntuacion = 1
            elif intencion == "negativo":
                puntuacion = 0
            else:
                return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        print(f"[DEBUG] Puntuación final asignada: {puntuacion}")


        # Analizar emoción solo si es entrada libre
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        # Guardar datos
        datos_guardados["puntuacion_apetito"] = puntuacion
        datos_guardados["apetito_texto"] = texto_usuario
        datos_guardados["emocion_apetito"] = emocion
        datos_guardados["confianza_emocion_apetito"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has notado cambios en tu apetito o en la cantidad de comida que tomas?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        if puntuacion == 1:
            siguiente = dialog_manager.obtener_detalle_apetito()
            mensaje = (
                "Gracias por compartirlo. Los cambios en el apetito pueden ser una señal importante de cómo nos sentimos.\n\n"
                f"{siguiente['mensaje']}"
            )
            return {
                "estado": siguiente["estado"],
                "mensaje": mensaje,
                "modo_entrada": siguiente["modo_entrada"],
                "sugerencias": siguiente.get("sugerencias", [])
            }, datos_guardados

        elif puntuacion == 0:
            siguiente = dialog_manager.obtener_mensaje_concentracion()
            mensaje = (
                "Está bien, comer con normalidad es una buena señal.\n\n"
                f"{siguiente['mensaje']}"
            )
            return {
                "estado": siguiente["estado"],
                "mensaje": mensaje,
                "modo_entrada": siguiente["modo_entrada"],
                "sugerencias": siguiente.get("sugerencias", [])
            }, datos_guardados

        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados


    # --- Detalle del Apetito ---
    if estado_actual == "detalle_apetito":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["detalle_apetito"] = texto_usuario
        datos_guardados["emocion_detalle_apetito"] = emocion
        datos_guardados["confianza_emocion_detalle_apetito"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Qué tipo de cambios has notado en tu apetito?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_concentracion()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por contármelo. Entender cómo afecta el apetito también es importante.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados

    # --- Preguntar Concentración ---
    if estado_actual == "preguntar_concentracion":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        texto_limpio = limpiar_texto(texto_usuario)

        # Solo mapear sugerencias exactas
        mapa_respuestas = {
            "sí, me cuesta concentrarme": 1,
            "no, me concentro bien": 0,
            "no estoy seguro": None
        }

        mapa_respuestas_limpio = {limpiar_texto(k): v for k, v in mapa_respuestas.items()}
        puntuacion = mapa_respuestas_limpio.get(texto_limpio)

        # Si no coincide con sugerencias, usar intención
        if puntuacion is None:
            intencion = detectar_intencion(texto_usuario)
            print(f"[DEBUG] Intención detectada: {intencion}")
            if intencion == "afirmativo":
                puntuacion = 1
            elif intencion == "negativo":
                puntuacion = 0
            else:
                return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        print(f"[DEBUG] Puntuación final asignada: {puntuacion}")

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["puntuacion_concentracion"] = puntuacion
        datos_guardados["concentracion_texto"] = texto_usuario
        datos_guardados["emocion_concentracion"] = emocion
        datos_guardados["confianza_emocion_concentracion"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Te ha costado concentrarte en actividades como leer, trabajar o seguir una conversación?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        if puntuacion == 1:
            siguiente = dialog_manager.obtener_detalle_concentracion()
            mensaje = (
                "Gracias por compartirlo. Es común que la falta de concentración acompañe a estados emocionales bajos.\n\n"
                f"{siguiente['mensaje']}"
            )
        elif puntuacion == 0:
            siguiente = dialog_manager.obtener_mensaje_agitacion()
            mensaje = (
                "Está bien, mantener una buena concentración es un buen indicador de estabilidad.\n\n"
                f"{siguiente['mensaje']}"
            )
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        return {
            "estado": siguiente["estado"],
            "mensaje": mensaje,
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Detalle de la Concentración ---
    if estado_actual == "detalle_concentracion":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["detalle_concentracion"] = texto_usuario
        datos_guardados["emocion_detalle_concentracion"] = emocion
        datos_guardados["confianza_emocion_detalle_concentracion"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Con qué actividades te cuesta más concentrarte?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_agitacion()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por compartirlo. La concentración es algo que puede verse muy afectado por nuestro estado emocional.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados

    # --- Preguntar Agitación ---
    if estado_actual == "preguntar_agitacion":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        texto_limpio = limpiar_texto(texto_usuario)

        # Solo mapear sugerencias exactas
        mapa_respuestas = {
            "sí, me siento inquieto": 1,
            "no, estoy tranquilo": 0,
            "no estoy seguro": None
        }

        mapa_respuestas_limpio = {limpiar_texto(k): v for k, v in mapa_respuestas.items()}
        puntuacion = mapa_respuestas_limpio.get(texto_limpio)

        # Si no coincide con sugerencias, usar intención
        if puntuacion is None:
            intencion = detectar_intencion(texto_usuario)
            print(f"[DEBUG] Intención detectada: {intencion}")
            if intencion == "afirmativo":
                puntuacion = 1
            elif intencion == "negativo":
                puntuacion = 0
            else:
                return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        print(f"[DEBUG] Puntuación final asignada: {puntuacion}")

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["puntuacion_agitacion"] = puntuacion
        datos_guardados["agitacion_texto"] = texto_usuario
        datos_guardados["emocion_agitacion"] = emocion
        datos_guardados["confianza_emocion_agitacion"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has notado que últimamente sientes inquietud o agitación?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        if puntuacion == 1:
            siguiente = dialog_manager.obtener_detalle_agitacion()
            mensaje = (
                "Gracias por compartirlo. A veces la inquietud puede ser difícil de explicar pero importante de reconocer.\n\n"
                f"{siguiente['mensaje']}"
            )
        elif puntuacion == 0:
            siguiente = dialog_manager.obtener_mensaje_antecedentes_generales()
            mensaje = (
                "Me alegra saber que no has notado inquietud últimamente.\n\n"
                f"{siguiente['mensaje']}"
            )
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        return {
            "estado": siguiente["estado"],
            "mensaje": mensaje,
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados

    # --- Detalle Agitación ---
    if estado_actual == "detalle_agitacion":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["detalle_agitacion"] = texto_usuario
        datos_guardados["emocion_detalle_agitacion"] = emocion
        datos_guardados["confianza_emocion_detalle_agitacion"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Cómo describirías esa inquietud que has sentido últimamente?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_antecedentes_generales()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por contármelo. La agitación puede tener un gran impacto en cómo nos sentimos en el día a día.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- APARTADO ANTECEDENTES ---
    # --- Preguntar Antecedentes Generales ---
    if estado_actual == "preguntar_antecedentes_generales":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["antecedentes_generales"] = texto_usuario
        datos_guardados["emocion_antecedentes_generales"] = emocion
        datos_guardados["confianza_emocion_antecedentes_generales"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Hay algo que suela desencadenar tu tristeza, como situaciones, pensamientos o preocupaciones?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_consecuentes_generales_1()
        mensaje = (
            "Gracias por compartirlo. Entender qué desencadena esas emociones es un paso importante para gestionarlas mejor.\n\n"
            f"{siguiente['mensaje']}"
        )

        return {
            "estado": siguiente["estado"],
            "mensaje": mensaje,
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Preguntar Consecuentes Generales 1 ---
    if estado_actual == "preguntar_consecuentes_generales_1":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["consecuentes_generales_1"] = texto_usuario
        datos_guardados["emocion_consecuentes_generales_1"] = emocion
        datos_guardados["confianza_emocion_consecuentes_generales_1"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="Cuando sientes tristeza, ¿qué sueles hacer? ¿Hay algo que te ayude como llamar a alguien, comer algo, etc.?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_consecuentes_generales_2()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por compartirlo. Saber cómo reaccionamos cuando nos sentimos tristes puede ayudarnos a comprender nuestras emociones.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Preguntar Consecuentes Generales 2 ---
    if estado_actual == "preguntar_consecuentes_generales_2":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["consecuentes_generales_2"] = texto_usuario
        datos_guardados["emocion_consecuentes_generales_2"] = emocion
        datos_guardados["confianza_emocion_consecuentes_generales_2"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has notado cambios en tu comportamiento cuando sientes tristeza? Por ejemplo, evitar situaciones.",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_impacto_diario()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por contármelo. Los cambios en el comportamiento pueden ser señales importantes de cómo estamos afrontando la tristeza.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- APARTADO IMPACTO EN LA VIDA DIARIA ---
    # --- Preguntar Impacto Diario ---
    if estado_actual == "preguntar_impacto_diario":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        texto_limpio = limpiar_texto(texto_usuario)

        mapa_respuestas = {
            "sí, ha afectado mi vida diaria": 1,
            "no, no ha afectado mi vida diaria": 0,
            "no estoy seguro": None
        }

        mapa_respuestas_limpio = {limpiar_texto(k): v for k, v in mapa_respuestas.items()}
        puntuacion = mapa_respuestas_limpio.get(texto_limpio)

        if puntuacion is None:
            intencion = detectar_intencion(texto_usuario)
            print(f"[DEBUG] Intención detectada: {intencion}")
            if intencion == "afirmativo":
                puntuacion = 1
            elif intencion == "negativo":
                puntuacion = 0
            else:
                return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        print(f"[DEBUG] Puntuación final asignada: {puntuacion}")

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["puntuacion_impacto_diario"] = puntuacion
        datos_guardados["impacto_diario_texto"] = texto_usuario
        datos_guardados["emocion_impacto_diario"] = emocion
        datos_guardados["confianza_emocion_impacto_diario"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Dirías que estos sentimientos han afectado tu vida diaria? Por ejemplo, en el trabajo, estudios, relaciones sociales o bienestar personal.",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        if puntuacion == 1:
            siguiente = dialog_manager.obtener_detalle_impacto_diario()
            mensaje = (
                "Gracias por compartirlo. Es importante identificar las áreas en las que estos sentimientos nos afectan.\n\n"
                f"{siguiente['mensaje']}"
            )
        elif puntuacion == 0:
            siguiente = dialog_manager.obtener_mensaje_estrategias_1()
            mensaje = (
                "Entiendo. Me alegra saber que no está teniendo un gran impacto en tu día a día.\n\n"
                f"{siguiente['mensaje']}"
            )
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        return {
            "estado": siguiente["estado"],
            "mensaje": mensaje,
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados

    # --- Detalle Impacto Diario ---
    if estado_actual == "detalle_impacto_diario":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        datos_guardados["detalle_impacto_diario"] = texto_usuario
        datos_guardados["emocion_detalle_impacto_diario"] = emocion
        datos_guardados["confianza_emocion_detalle_impacto_diario"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿En qué aspectos sientes más dificultades en tu día a día debido a estos sentimientos?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_estrategias_1()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por contármelo. Reconocer los efectos en tu día a día nos ayuda a trabajar sobre ellos de forma más precisa.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- APARTADO ESTRATEGIAS DE AFRONTAMIENTO ---
    # --- Preguntar Estrategias de Afrontamiento ---
    if estado_actual == "preguntar_estrategias_1":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Analizar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        # Guardar respuesta
        datos_guardados["estrategias_1"] = texto_usuario
        datos_guardados["emocion_estrategias_1"] = emocion
        datos_guardados["confianza_emocion_estrategias_1"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Qué cosas sueles hacer para lidiar con la tristeza?",
            respuesta_usuario=texto_usuario
        )

        siguiente = dialog_manager.obtener_mensaje_estrategias_2()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por compartirlo. Saber tus recursos de afrontamiento es muy valioso.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Preguntar Estrategias de Afrontamiento ---
    if estado_actual == "preguntar_estrategias_2":
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Analizar emoción
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza = resultado_emocional.get("confianza", "0%")

        # Guardar respuesta
        datos_guardados["estrategias_2"] = texto_usuario
        datos_guardados["emocion_estrategias_2"] = emocion
        datos_guardados["confianza_emocion_estrategias_2"] = confianza

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Existen actividades o estrategias que te ayuden a sentirte mejor cuando sientes tristeza?",
            respuesta_usuario=texto_usuario
        )

        # Obtener nombre del usuario
        nombre = datos_guardados.get("nombre_usuario", "amigo/a")

        # Transición al cierre con nombre personalizado
        siguiente = dialog_manager.obtener_mensaje_percepcion_empatia()
        return {
            "estado": siguiente["estado"],
            "mensaje": (
                "Gracias por compartirlo. Tener identificadas estas estrategias puede ayudarte a gestionar mejor los momentos difíciles.\n\n"
                f"{siguiente['mensaje']}"
            ),
            "modo_entrada": siguiente["modo_entrada"],
            "sugerencias": siguiente.get("sugerencias", [])
        }, datos_guardados


    # --- Preguntar percepción de empatía del chatbot ---
    if estado_actual == "preguntar_percepcion_empatia":
        texto_limpio = limpiar_texto(texto_usuario)

        if not texto_limpio.isdigit() or int(texto_limpio) not in range(0, 11):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        puntuacion_empatia = int(texto_limpio)
        datos_guardados["puntuacion_empatia"] = puntuacion_empatia

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Cómo calificarías la empatía del chatbot (0 a 10)?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion_empatia
        )

        # 1. Generar PDF del informe
        nombre_pdf = f"{session_id}.pdf"
        ruta_pdf = os.path.join("static", "informes", nombre_pdf)
        os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)
        generar_pdf_informe(session_id, ruta_pdf)

        # 2. Construir URL pública del PDF
        url_pdf = f"http://localhost:8000/static/informes/{nombre_pdf}"

        # 3. Mensaje de cierre con enlace al informe
        nombre = datos_guardados.get("nombre_usuario", "usuario")
        cierre = dialog_manager.obtener_mensaje_cierre(nombre)
        mensaje_final = (
            f"{cierre['mensaje']}\n\n"
            f"Puedes descargar tu informe desde el siguiente enlace:\n{url_pdf}"
        )

        return {
            "estado": cierre["estado"],
            "mensaje": mensaje_final,
            "modo_entrada": cierre["modo_entrada"],
            "sugerencias": cierre.get("sugerencias", [])
        }, datos_guardados



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
