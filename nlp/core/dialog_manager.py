# Funciones que controlan los mensajes y las fases del asistente virtual

# -------------------- Fase de Presentación --------------------
def obtener_mensaje_presentacion() -> dict:
    return {
        "estado": "presentacion",
        "mensaje": (
            "¡Hola! Soy un asistente virtual diseñado para ayudarte a reflexionar sobre tu estado emocional.\n"
            "Te haré algunas preguntas para entender mejor cómo te has sentido últimamente.\n"
            "Esta evaluación no sustituye a una consulta profesional, pero puede ayudarte a poner en palabras lo que estás experimentando.\n\n"
            "¿Te parece bien continuar con la evaluación?\n\n"
            "Puedes responder, por ejemplo: 'Sí, quiero seguir' o 'Prefiero no hacerlo'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Sí", "No"]
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
            "Puedes responder de forma aproximada, por ejemplo: 'Todos los días', 'De vez en cuando', 'Rara vez'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Todos los días", "De vez en cuando", "Rara vez"]
    }

# -------------------- Exploración: Duración --------------------
def obtener_mensaje_duracion_tristeza() -> dict:
    return {
        "estado": "duracion_tristeza",
        "mensaje": (
            "Gracias por compartirlo. Ahora me gustaría saber cuánto tiempo suele durarte esa tristeza una vez aparece.\n\n"
            "Puede ser algo breve o prolongado. Me interesa una estimación aproximada, no hace falta que sea exacta.\n\n"
            "Por ejemplo: 'Unas horas', 'Uno o dos días', 'Más de una semana', etc."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Unas horas", "Uno o dos días", "Más de una semana"]
    }


# -------------------- Exploración: Intensidad --------------------
def obtener_mensaje_intensidad_tristeza() -> dict:
    return {
        "estado": "intensidad_tristeza",
        "mensaje": (
            "Por último, ¿qué tan intensa suele ser esa tristeza cuando aparece?\n\n"
            "Por favor, indícalo en una escala del 1 (poco intensa) al 10 (muy intensa).\n"
            "Puedes escribir, por ejemplo: '3', '7', '10'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["3", "7", "10"]
    }
