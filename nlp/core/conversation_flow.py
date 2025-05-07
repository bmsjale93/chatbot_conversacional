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
from core.database import guardar_interaccion_completa
from core.cleaner import limpiar_texto
from utils.extract_name import extraer_nombre
from utils.respuestas_ideacion_suicidio import respuestas_ideacion_suicidio
import re

def detectar_emocion(texto_usuario: str) -> str:
    """
    Detecta la emoción principal del texto, utilizando caché si está disponible.
    """
    cached = obtener_cache(texto_usuario)
    if cached and "estado_emocional" in cached:
        return cached["estado_emocional"]

    resultado = analizar_sentimiento(texto_usuario)
    guardar_cache(texto_usuario, resultado)
    return resultado.get("estado_emocional", "neutral")

# Constantes de estado
FIN = "fin"
ERROR = "error"
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
    "esperar_siguiente_pregunta": dialog_manager.obtener_mensaje_esperar_siguiente_pregunta,
}


def procesar_mensaje(session_id: str, texto_usuario: str, estado_actual: str, datos_guardados: dict) -> Tuple[dict, dict]:

    # --- Validación global de mensaje vacío ---
    if not texto_usuario or not texto_usuario.strip():
        respuesta_base_fn = ESTADOS_DIALOG_MANAGER.get(estado_actual)

        if respuesta_base_fn:
            # Comprobar si la función acepta argumentos
            try:
                base = respuesta_base_fn(datos_guardados)
            except TypeError:
                base = respuesta_base_fn()
            return {
                "estado": estado_actual,
                "mensaje": (
                    "Por favor, selecciona una opción o escribe algo antes de continuar."
                ),
                "modo_entrada": base.get("modo_entrada", "texto_libre"),
                "sugerencias": base.get("sugerencias", [])
            }, datos_guardados

        # Fallback genérico si no se encuentra el estado
        return {
            "estado": estado_actual,
            "mensaje": "Por favor, escribe algo antes de continuar.",
            "modo_entrada": "mixto",
            "sugerencias": []
        }, datos_guardados



    # --- Fase de presentación ---
    if estado_actual == "presentacion":
        respuesta = dialog_manager.obtener_mensaje_presentacion()
        respuesta["estado"] = "consentimiento"
        return respuesta, datos_guardados

    # --- Consentimiento ---
    if estado_actual == "consentimiento":
        texto_limpio = limpiar_texto(texto_usuario).lower()

        # 1. Detectar ambigüedad explícita
        if detectar_ambiguedad(texto_usuario):
            return generar_respuesta_aclaratoria("consentimiento"), datos_guardados

        # 2. Reglas manuales para rechazo explícito
        respuestas_negativas_explicitamente = [
            "no", "no quiero continuar", "no, prefiero no continuar",
            "prefiero no continuar", "no deseo continuar"
        ]
        if texto_limpio in respuestas_negativas_explicitamente:
            respuesta = dialog_manager.obtener_mensaje_consentimiento_rechazado()
            return respuesta, datos_guardados

        # 3. Clasificador de intención
        intencion = detectar_intencion(texto_usuario)

        if intencion == "afirmativo":
            respuesta = dialog_manager.obtener_mensaje_nombre()
            respuesta["estado"] = "preguntar_nombre"
        elif intencion == "negativo":
            respuesta = dialog_manager.obtener_mensaje_consentimiento_rechazado()
        else:
            respuesta = dialog_manager.obtener_mensaje_presentacion()
            respuesta["estado"] = "consentimiento"

        return respuesta, datos_guardados

    # --- Preguntar nombre ---
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
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

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

        datos_guardados["puntuacion_desesperanza"] = puntuacion

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Te resulta difícil encontrar algo que te ilusione o motive al pensar en el futuro?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        mensaje_base = "Gracias por contar esto. A veces sentir que el futuro carece de ilusión puede ser una señal de que necesitamos apoyo."
        mensaje_empatico = generar_respuesta_empatica(mensaje_base, tipo=emocion_detectada)

        respuesta = dialog_manager.obtener_mensaje_inutilidad()
        respuesta["mensaje"] = f"{mensaje_empatico}\n\n{respuesta['mensaje']}"
        return respuesta, datos_guardados


    # --- Preguntar sentimientos de inutilidad ---
    if estado_actual == "preguntar_inutilidad":
        texto_limpio = limpiar_texto(texto_usuario)

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        # Detección de intención y emoción
        intencion = detectar_intencion(texto_limpio)
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()

        if intencion == "afirmativo":
            puntuacion = 1
            datos_guardados["inutilidad"] = True
            datos_guardados["puntuacion_inutilidad"] = puntuacion
            asignar_puntuacion(session_id, "inutilidad", str(puntuacion))
            respuesta_base = dialog_manager.obtener_detalle_inutilidad()
            respuesta = {
                "estado": respuesta_base["estado"],
                "mensaje": respuesta_base["mensaje"],
                "modo_entrada": respuesta_base.get("modo_entrada", "texto_libre"),
                "sugerencias": respuesta_base.get("sugerencias", [])
            }
        elif intencion == "negativo":
            puntuacion = 0
            datos_guardados["inutilidad"] = False
            datos_guardados["puntuacion_inutilidad"] = puntuacion
            asignar_puntuacion(session_id, "inutilidad", str(puntuacion))
            respuesta_base = dialog_manager.obtener_mensaje_ideacion_suicida()
            respuesta = {
                "estado": respuesta_base["estado"],
                "mensaje": f"{mensaje_empatico}\n\n{respuesta_base['mensaje']}",
                "modo_entrada": respuesta_base.get("modo_entrada", "texto_libre"),
                "sugerencias": respuesta_base.get("sugerencias", [])
            }
        else:
            return generar_respuesta_aclaratoria(estado_actual), datos_guardados

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿En los últimos días has sentido que no eres suficiente?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        mensaje_base = "A veces podemos ser muy críticos con nosotros mismos, sobre todo en momentos de vulnerabilidad emocional."
        mensaje_empatico = generar_respuesta_empatica(mensaje_base, tipo=emocion_detectada)

        respuesta["mensaje"] = f"{mensaje_empatico}\n\n{respuesta['mensaje']}"
        return respuesta, datos_guardados


    # --- Detalle situaciones de inutilidad ---
    if estado_actual == "detalle_inutilidad":
        # Detectar emoción y score
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza_emocion = resultado_emocional.get("confianza", "0%")

        # Generar mensaje empático en base a la emoción
        mensaje_base = (
            "Gracias por abrirte y contarme en qué momentos te sientes así. "
            "Es importante reconocer esas situaciones para poder abordarlas."
        )
        mensaje_empatico = generar_respuesta_empatica(mensaje_base, tipo=emocion_detectada)

        # Guardar interacción completa incluyendo emoción detectada
        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿En qué situaciones sientes que no eres suficiente?",
            respuesta_usuario=texto_usuario,
            puntuacion=None  # No se asigna puntuación explícita aquí
        )

        datos_guardados["situaciones_inutilidad"] = texto_usuario
        datos_guardados["emocion_ultima_respuesta"] = emocion_detectada
        datos_guardados["confianza_emocion"] = confianza_emocion

        # Preparar respuesta
        respuesta = dialog_manager.obtener_mensaje_ideacion_suicida()
        respuesta["mensaje"] = f"{mensaje_empatico}\n\n{respuesta['mensaje']}"
        return respuesta, datos_guardados


    # --- Preguntar ideación suicida ---
    if estado_actual == "preguntar_ideacion_suicida":
        texto_limpio = limpiar_texto(texto_usuario)
        texto_bajo = texto_limpio.lower()

        if detectar_ambiguedad(texto_limpio):
            return generar_respuesta_aclaratoria_ideacion(estado_actual), datos_guardados

        # Detectar emoción y confianza
        resultado_emocional = analizar_sentimiento(texto_usuario)
        emocion_detectada = resultado_emocional.get("estado_emocional", "neutral").lower()
        confianza_emocion = resultado_emocional.get("confianza", "0%")

        puntuacion = None
        mensaje = None

        for frase in respuestas_ideacion_suicidio["puntuacion_3"]:
            if frase in texto_bajo:
                puntuacion = 3
                mensaje = (
                    "Gracias por compartirlo. Lamento mucho que sea así, imagino que estás pasando por una situación difícil.\n\n"
                    "Lo más adecuado es que contactes ahora mismo con profesionales humanos. Por favor, ponte en contacto con las personas que pueden ayudarte:\n\n"
                    "- 📞 024 (Atención al suicidio - Cruz Roja)\n"
                    "- 📞 717 00 37 17 (Teléfono de la esperanza)\n"
                    "- 📞 112 (Emergencias)"
                )
                break

        if puntuacion is None:
            for frase in respuestas_ideacion_suicidio["puntuacion_2"]:
                if frase in texto_bajo:
                    puntuacion = 2
                    mensaje = (
                        "Gracias por tu sinceridad. Entiendo que compartir esto no es fácil.\n\n"
                        "Si en algún momento estos pensamientos se vuelven más intensos o difíciles de manejar, por favor considera hablar con un profesional de salud mental.\n"
                        "Tu bienestar es muy importante. Seguimos adelante cuando estés preparado/a, sin presión."
                    )
                    break

        if puntuacion is None:
            for frase in respuestas_ideacion_suicidio["puntuacion_1"]:
                if frase in texto_bajo:
                    puntuacion = 1
                    mensaje = (
                        "Gracias por compartir algo tan delicado. No estás solo/a en sentirte así en ciertos momentos.\n\n"
                        "Reconocer estos pensamientos, incluso sin intención, ya es un paso importante para cuidar tu salud emocional.\n"
                        "Seguimos cuando estés listo/a, estoy aquí para acompañarte en este proceso."
                    )
                    break

        if puntuacion is None:
            for frase in respuestas_ideacion_suicidio["puntuacion_0"]:
                if frase in texto_bajo:
                    puntuacion = 0
                    mensaje = (
                        "Gracias por tu respuesta. Me alegra saber que no has tenido pensamientos de ese tipo últimamente.\n\n"
                        "Es importante reconocer estos momentos en los que nos sentimos emocionalmente estables. "
                        "Vamos a continuar cuando te sientas preparado/a."
                    )
                    break

        if puntuacion is None:
            return generar_respuesta_aclaratoria_ideacion(estado_actual), datos_guardados

        # Guardar datos
        datos_guardados["puntuacion_ideacion_suicida"] = puntuacion
        datos_guardados["ideacion_suicida_texto"] = texto_usuario
        datos_guardados["emocion_ultima_respuesta"] = emocion_detectada
        datos_guardados["confianza_emocion"] = confianza_emocion

        guardar_interaccion_completa(
            session_id=session_id,
            estado=estado_actual,
            pregunta="¿Has tenido pensamientos relacionados con el suicidio en las últimas dos semanas?",
            respuesta_usuario=texto_usuario,
            puntuacion=puntuacion
        )

        respuesta = dialog_manager.obtener_mensaje_esperar_siguiente_pregunta()
        respuesta["mensaje"] = mensaje
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
