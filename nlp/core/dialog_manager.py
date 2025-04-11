# Funciones que controlan los mensajes y las fases del asistente virtual

# -------------------- Fase de Presentación --------------------
def obtener_mensaje_presentacion():
    return {
        "estado": "presentacion",
        "mensaje": (
            "¡Hola! Soy un asistente virtual diseñado para ayudarte a evaluar tu estado de ánimo. "
            "Te haré algunas preguntas para conocer cómo te has sentido en los últimos días. "
            "Esta evaluación no sustituye a una consulta profesional y su único propósito es recopilar información "
            "de manera clara y organizada. Recuerda que tu información será tratada con confidencialidad.\n\n"
            "¿Estás de acuerdo en continuar con la evaluación?\n\n"
            "Puedes responder libremente, por ejemplo: 'Sí, quiero seguir' o 'Prefiero no hacerlo'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Sí", "No"]
    }

# -------------------- Fase de Cierre si no acepta --------------------
def obtener_mensaje_consentimiento_rechazado():
    return {
        "estado": "fin",
        "mensaje": (
            "Entiendo tu decisión. Gracias por tu tiempo. "
            "Si en otro momento quieres hablar, estaré disponible."
        ),
        "modo_entrada": "fin",
        "sugerencias": []
    }

# -------------------- Fase de Solicitud de Nombre --------------------
def obtener_mensaje_nombre():
    return {
        "estado": "preguntar_nombre",
        "mensaje": (
            "¿Con qué nombre o seudónimo puedo dirigirme a ti?\n\n"
            "Puedes responder libremente, por ejemplo: 'Llamame Alex'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }

# -------------------- Fase de Preguntar Identidad --------------------
def obtener_mensaje_identidad(nombre_usuario: str):
    return {
        "estado": "preguntar_identidad",
        "mensaje": (
            f"Un placer conocerte, {nombre_usuario}. "
            "¿Qué etiqueta identifica mejor tu identidad?\n\n"
            "Puedes responder de forma libre, por ejemplo: 'Masculino', 'Femenino' o 'No binario'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Masculino", "Femenino", "No binario"]
    }

# -------------------- Fase de Inicio de Exploración Emocional --------------------


def obtener_mensaje_exploracion_tristeza(nombre_usuario: str):
    return {
        "estado": "inicio_exploracion_tristeza",
        "mensaje": (
            f"Gracias, {nombre_usuario}. Ahora voy a hacerte algunas preguntas sobre cómo te has sentido "
            "últimamente. No hay respuestas correctas o incorrectas. Responde de la forma más honesta posible.\n\n"
            "Para empezar, ¿dirías que has experimentado tristeza recientemente?\n\n"
            "Puedes responder libremente, como por ejemplo: 'Sí, me he sentido muy triste' o 'No, en general he estado bien'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": ["Sí", "No"]
    }

# -------------------- Fase de Frecuencia de Tristeza --------------------


def obtener_mensaje_frecuencia_tristeza():
    return {
        "estado": "frecuencia_tristeza",
        "mensaje": (
            "¿Con qué frecuencia sueles experimentar síntomas de tristeza?\n\n"
            "Responde libremente: 'Todos los días', 'De vez en cuando', 'Rara vez', etc."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }

# -------------------- Fase de Duración de la Tristeza --------------------
def obtener_mensaje_duracion_tristeza():
    return {
        "estado": "duracion_tristeza",
        "mensaje": (
            "¿Cuánto tiempo tardas en sentirte mejor cuando experimentas tristeza?\n\n"
            "Por ejemplo: 'Un par de horas', 'Dos días', 'Semanas'."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }

# -------------------- Fase de Intensidad de Tristeza --------------------
def obtener_mensaje_intensidad_tristeza():
    return {
        "estado": "intensidad_tristeza",
        "mensaje": (
            "Cuando sientes tristeza, ¿cómo de intenso es tu malestar?\n\n"
            "Por favor, indícalo en una escala del 1 (poco intenso) al 10 (muy intenso).\n"
            "Puedes escribir, por ejemplo: '6', '8', '10', etc."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }
