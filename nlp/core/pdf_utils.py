from datetime import datetime, timezone

# Diccionario con mapeo de claves a preguntas completas
MAPA_PREGUNTAS_PDF = {
    "consentimiento": "¿Estás de acuerdo en continuar con esta evaluación emocional?",
    "preguntar_nombre": "¿Con qué nombre o seudónimo puedo dirigirme a ti?",
    "preguntar_identidad": "¿Qué etiqueta identifica mejor tu identidad?",
    "respuesta_tristeza": "¿Has experimentado tristeza recientemente?",
    "frecuencia_tristeza": "¿Con qué frecuencia sueles experimentar tristeza?",
    "duracion_tristeza": "¿Cuánto tiempo dura generalmente esa tristeza?",
    "intensidad_tristeza": "Cuando sientes tristeza, ¿cómo de intensa es?",
    "anhedonia": "¿Has notado pérdida de interés o placer en actividades que antes disfrutabas?",
    "actividades_sin_disfrute": "¿Qué actividades has dejado de disfrutar?",
    "desesperanza": "¿Te resulta difícil encontrar algo que te ilusione o motive al pensar en el futuro?",
    "inutilidad": "¿En los últimos días has sentido que no eres suficiente?",
    "ideacion_suicida_texto": "¿Has tenido pensamientos relacionados con el suicidio en las últimas dos semanas?",
    "fatiga_texto": "¿Has notado últimamente que te falta energía o te cansas con más facilidad de lo habitual?",
    "sueno_texto": "¿Has notado últimamente cambios o dificultades con tu sueño?",
    "detalle_sueno": "¿Qué tipo de dificultades has notado con tu sueño?",
    "apetito_texto": "¿Has notado cambios en tu apetito o en la cantidad de comida que tomas?",
    "detalle_apetito": "¿Qué tipo de cambios has notado en tu apetito?",
    "concentracion_texto": "¿Te ha costado concentrarte en actividades como leer, trabajar o seguir una conversación?",
    "detalle_concentracion": "¿Con qué actividades te cuesta más concentrarte?",
    "agitacion_texto": "¿Has notado que últimamente sientes inquietud o agitación?",
    "detalle_agitacion": "¿Cómo describirías esa inquietud que has sentido últimamente?",
    "antecedentes_generales": "¿Hay algo que suela desencadenar tu tristeza, como situaciones, pensamientos o preocupaciones?",
    "consecuentes_generales_1": "Cuando sientes tristeza, ¿qué sueles hacer?",
    "consecuentes_generales_2": "¿Has notado cambios en tu comportamiento cuando sientes tristeza?",
    "impacto_diario_texto": "¿Dirías que estos sentimientos han afectado tu vida diaria?",
    "detalle_impacto_diario": "¿En qué aspectos sientes más dificultades en tu día a día?",
    "estrategias_1": "¿Qué cosas sueles hacer para lidiar con la tristeza?",
    "estrategias_2": "¿Existen actividades o estrategias que te ayuden a sentirte mejor cuando sientes tristeza?",
    "puntuacion_empatia": "¿Cómo calificarías la empatía del chatbot (0 a 10)?"
}

# Claves que contienen booleanos pero tienen texto original del usuario asociado
CLAVES_BOOLEANAS_CON_TEXTO = {
    "anhedonia": "anhedonia"
}

def construir_interacciones_para_pdf(datos_guardados: dict) -> list:
    """
    Construye una lista de interacciones a partir de datos_guardados,
    utilizando preguntas reales desde el mapa y mostrando el texto original si es necesario.
    """
    interacciones = []

    for clave, valor in datos_guardados.items():
        if clave not in MAPA_PREGUNTAS_PDF:
            continue

        pregunta = MAPA_PREGUNTAS_PDF[clave]
        base = clave.replace("_texto", "").replace("respuesta_", "").replace("detalle_", "")

        emocion = datos_guardados.get(f"emocion_{base}", "")
        confianza = datos_guardados.get(f"confianza_emocion_{base}", "")
        puntuacion = datos_guardados.get(f"puntuacion_{base}", "")

        # Sustituir valor booleano por el texto original del usuario si es necesario
        if clave in CLAVES_BOOLEANAS_CON_TEXTO:
            texto_usuario = datos_guardados.get("anhedonia_texto", str(valor))
        else:
            texto_usuario = str(valor)

        interacciones.append({
            "pregunta": pregunta,
            "respuesta_usuario": texto_usuario,
            "emocion": emocion,
            "confianza_emocion": confianza,
            "puntuacion": puntuacion,
            "timestamp": datetime.now(timezone.utc)
        })

    return interacciones
