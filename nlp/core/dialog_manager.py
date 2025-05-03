# Funciones que controlan los mensajes y las fases del asistente virtual

# -------------------- Fase de Presentación --------------------
def obtener_mensaje_presentacion() -> dict:
    return {
        "estado": "presentacion",
        "mensaje": (
            "¡Hola! Soy un asistente virtual diseñado para ayudar en la evaluación de tu estado de ánimo.\n\n"
            "Te haré algunas preguntas para conocer cómo te has sentido en los últimos días. "
            "Esta evaluación no sustituye a una consulta profesional y su único propósito es recopilar información de manera clara y organizada.\n\n"
            "Ten en cuenta que soy un asistente virtual o chatbot, no un psicólogo humano, por lo que te pido por favor que escribas respuestas concisas.\n\n"
            "Antes de comenzar, necesito tu consentimiento. Recuerda que, en cualquier caso, tu información será tratada con confidencialidad.\n\n"
            "¿Estás de acuerdo en continuar con la evaluación?"
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Sí, estoy de acuerdo", "No, prefiero no continuar"]
    }


def obtener_mensaje_consentimiento_rechazado() -> dict:
    return {
        "estado": "fin",
        "mensaje": (
            "Entiendo tu decisión. Gracias por tu tiempo. "
            "Si en otro momento quieres hablar, estaré disponible para escucharte."
        ),
        "modo_entrada": "fin",
        "sugerencias": []
    }

# -------------------- Fase de Solicitud de Nombre --------------------
def obtener_mensaje_nombre() -> dict:
    return {
        "estado": "preguntar_nombre",
        "mensaje": (
            "¿Con qué nombre o seudónimo puedo dirigirme a ti?\n\n"
            "Puedes escribirme tu nombre real o cualquier nombre con el que te sientas cómodo/a, por ejemplo: 'Alejandro', 'María', 'Alex'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }

# -------------------- Fase de Pregunta de Identidad --------------------
def obtener_mensaje_identidad(nombre_usuario: str) -> dict:
    return {
        "estado": "preguntar_identidad",
        "mensaje": (
            f"Un placer conocerte, {nombre_usuario}.\n"
            "¿Qué etiqueta identifica mejor tu identidad?\n\n"
            "Puedes responder libremente, por ejemplo: 'Masculino', 'Femenino' o 'No binario'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Masculino", "Femenino", "No binario"]
    }

# -------------------- Inicio de Exploración Emocional --------------------
def obtener_mensaje_exploracion_tristeza(nombre_usuario: str) -> dict:
    return {
        "estado": "inicio_exploracion_tristeza",
        "mensaje": (
            f"Gracias, {nombre_usuario}. Ahora voy a hacerte algunas preguntas sobre cómo te has sentido últimamente.\n"
            "No hay respuestas correctas o incorrectas. Lo importante es que respondas con sinceridad, según tu experiencia.\n\n"
            "Para empezar, ¿dirías que has sentido tristeza o bajones emocionales en los últimos días?\n\n"
            "Puedes responder, por ejemplo: 'Sí, me he sentido muy triste' o 'No, en general me he sentido bien'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Sí, me he sentido triste", "No, me he sentido bien", "No estoy seguro"]
    }

# -------------------- Exploración: Frecuencia --------------------
def obtener_mensaje_frecuencia_tristeza() -> dict:
    return {
        "estado": "frecuencia_tristeza",
        "mensaje": (
            "Gracias por compartirlo. Ahora me gustaría saber con qué frecuencia sueles experimentar esa tristeza.\n\n"
            "No es necesario que la respuesta sea exacta, solo una idea general. Puedes usar expresiones como:\n"
            "'Todos los días', 'Muy seguido', 'De vez en cuando', 'Casi nunca', etc."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": [
            "Todos los días [10]",
            "Muy seguido [8]",
            "A menudo [7]",
            "De vez en cuando [5]",
            "Pocas veces [3]",
            "Casi nunca [2]",
            "Nunca [1]"
        ]
    }

# -------------------- Exploración: Duración --------------------
def obtener_mensaje_duracion_tristeza() -> dict:
    return {
        "estado": "duracion_tristeza",
        "mensaje": (
            "Gracias por compartirlo. Me gustaría saber cuánto tiempo suele durarte esa tristeza cuando aparece.\n\n"
            "Puede durar unos instantes, horas, días o incluso semanas. No te preocupes por ser preciso, con una estimación basta.\n"
            "Por ejemplo: 'Unas horas', 'Un par de días', 'Una semana', 'Más de un mes', etc."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": [
            "Unas horas [2]",
            "Un día [3]",
            "Un par de días [4]",
            "Una semana [5]",
            "Dos semanas [6]",
            "Varias semanas [8]",
            "Más de un mes [10]"
        ]
    }

# -------------------- Exploración: Intensidad --------------------
def obtener_mensaje_intensidad_tristeza() -> dict:
    return {
        "estado": "intensidad_tristeza",
        "mensaje": (
            "Por último, ¿cómo describirías la intensidad de esa tristeza cuando aparece?\n\n"
            "Puedes usar una escala del 1 (muy leve) al 10 (muy intensa), o expresarlo de forma aproximada, como:\n"
            "'Creo que un 3', 'Más o menos un 7', 'Entre 8 y 9', etc."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["3", "5", "8", "10"]
    }


# -------------------- Síntomas físicos y conductuales --------------------

def obtener_mensaje_anhedonia() -> dict:
    return {
        "estado": "preguntar_anhedonia",
        "mensaje": (
            "A veces, lo que antes disfrutábamos deja de parecernos interesante o emocionante.\n\n"
            "¿Has notado si en los últimos días has perdido el interés o el placer en algunas actividades que solías disfrutar?\n\n"
            "Puedes responder, por ejemplo: 'Sí, ya no disfruto de algunas cosas' o 'No, sigo disfrutando igual'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Sí, he perdido interés", "No, sigo disfrutando igual"]
    }

def obtener_mensaje_anhedonia_profunda() -> dict:
    return {
        "estado": "detalle_anhedonia",
        "mensaje": (
            "Gracias por compartirlo. ¿Podrías decirme qué actividades específicas has dejado de disfrutar recientemente?\n"
            "Esto me ayuda a entender mejor en qué áreas has notado el cambio."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Salir con amigos", "Escuchar música", "Hacer deporte"]
    }


