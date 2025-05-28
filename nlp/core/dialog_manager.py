from utils.destacar import destacar_pregunta_binaria

# Funciones que controlan los mensajes y las fases del asistente virtual

# -------------------- Fase de Presentación --------------------
def obtener_mensaje_presentacion() -> dict:
    return {
        "estado": "presentacion",
        "mensaje": destacar_pregunta_binaria (
            "¡Hola! Soy un asistente virtual diseñado para ayudar en la evaluación de tu estado de ánimo.\n\n"
            "Te haré algunas preguntas para conocer cómo te has sentido en los últimos días. "
            "Esta evaluación no sustituye a una consulta profesional y su único propósito es recopilar información de manera clara y organizada.\n\n"
            "Ten en cuenta que soy un asistente virtual o chatbot, no un psicólogo humano, por lo que te pido por favor que escribas respuestas concisas.\n\n"
            "Antes de comenzar, necesito tu consentimiento. Recuerda que, en cualquier caso, tu información será tratada con confidencialidad.\n\n"
            "¿Estás de acuerdo en continuar con la evaluación?"
        ),
        "modo_entrada": "mixto",
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
            "Puedes escribirme tu nombre real o cualquier nombre con el que te sientas cómodo/a, por ejemplo: 'Alejandro', 'María', 'Juan'."
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
        "modo_entrada": "mixto",
        "sugerencias": ["Masculino", "Femenino", "No binario"]
    }

# -------------------- Inicio de Exploración Emocional --------------------
def obtener_mensaje_exploracion_tristeza(nombre_usuario: str) -> dict:
    return {
        "estado": "inicio_exploracion_tristeza",
        "mensaje": destacar_pregunta_binaria (
            f"Gracias, {nombre_usuario}. Ahora voy a hacerte algunas preguntas sobre cómo te has sentido últimamente.\n"
            "No hay respuestas correctas o incorrectas. Lo importante es que respondas con sinceridad, según tu experiencia.\n\n"
            "Para empezar, ¿dirías que has sentido tristeza o bajones emocionales en los últimos días?\n\n"
            "Puedes responder, por ejemplo: 'Sí, me he sentido muy triste' o 'No, en general me he sentido bien'."
        ),
        "modo_entrada": "mixto",
        "sugerencias": ["Sí, me he sentido triste", "No, me he sentido bien", "No estoy seguro"]
    }

# -------------------- Exploración: Frecuencia --------------------
def obtener_mensaje_frecuencia_tristeza() -> dict:
    return {
        "estado": "frecuencia_tristeza",
        "mensaje": (
            "Gracias por compartirlo. Ahora me gustaría saber con qué frecuencia sueles experimentar esa tristeza.\n\n"
            "Selecciona la opción que mejor refleje tu experiencia. No te preocupes por ser exacto, solo una estimación general."
        ),
        "modo_entrada": "sugerencias",  # Solo se permite elegir
        "sugerencias": [
            "Todos los días",
            "Casi todos los días",
            "Muy seguido",
            "A menudo",
            "Algunas veces por semana",
            "De vez en cuando",
            "Con poca frecuencia",
            "Pocas veces",
            "Casi nunca",
            "Nunca"
        ]
    }

# -------------------- Exploración: Duración --------------------
def obtener_mensaje_duracion_tristeza() -> dict:
    return {
        "estado": "duracion_tristeza",
        "mensaje": (
            "Gracias por compartirlo. Me gustaría saber cuánto tiempo suele durarte esa tristeza cuando aparece.\n\n"
            "Selecciona una opción que refleje lo que sueles experimentar."
        ),
        "modo_entrada": "sugerencias",  # Solo se permite elegir
        "sugerencias": [
            "Momentos puntuales",
            "Unas horas",
            "Más de 6 horas",
            "Un día o más",
            "Entre tres y cinco días",
            "Una semana",
            "Poco más de una semana",
            "Dos semanas",
            "Varias semanas",
            "Un mes o más"
        ]
    }

# -------------------- Exploración: Intensidad --------------------
def obtener_mensaje_intensidad_tristeza() -> dict:
    return {
        "estado": "intensidad_tristeza",
        "mensaje": (
            "Por último, ¿cómo describirías la intensidad de esa tristeza cuando aparece?\n\n"
            "Selecciona un número del 1 (muy leve) al 10 (muy intensa)."
        ),
        "modo_entrada": "sugerencias",  # Solo selección
        "sugerencias": [str(i) for i in range(1, 11)]
    }

# -------------------- Síntomas físicos y conductuales --------------------
def obtener_mensaje_anhedonia() -> dict:
    return {
        "estado": "preguntar_anhedonia",
        "mensaje": destacar_pregunta_binaria (
            "A veces, lo que antes disfrutábamos deja de parecernos interesante o emocionante.\n\n"
            "¿Has notado si en los últimos días has perdido el interés o el placer en algunas actividades que solías disfrutar?\n\n"
            "Puedes responder, por ejemplo: 'Sí, ya no disfruto de algunas cosas' o 'No, sigo disfrutando igual'."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Sí, he perdido interés",
            "No, sigo disfrutando igual",
            "No lo sé"
        ]
    }


def obtener_mensaje_anhedonia_profunda() -> dict:
    return {
        "estado": "detalle_anhedonia",
        "mensaje": (
            "¿Podrías decirme qué actividades específicas has dejado de disfrutar recientemente?\n"
            "Esto me ayuda a entender mejor en qué áreas has notado el cambio."
        ),
        "modo_entrada": "mixto",
        "sugerencias": ["Salir con amigos", "Escuchar música", "Hacer deporte"]
    }

def obtener_mensaje_desesperanza() -> dict:
    return {
        "estado": "preguntar_desesperanza",
        "mensaje": destacar_pregunta_binaria (
            "Cuando piensas en el futuro, ¿te resulta difícil encontrar algo que te ilusione o motive?\n\n"
            "Puedes responder con sinceridad, por ejemplo: 'Sí, últimamente nada me motiva' o 'No, tengo cosas que me ilusionan'."
        ),
        "modo_entrada": "mixto",
        "sugerencias": ["Sí, me cuesta ver el futuro con ilusión", "No, tengo metas", "No estoy seguro"]
    }

def obtener_mensaje_inutilidad() -> dict:
    return {
        "estado": "preguntar_inutilidad",
        "mensaje": destacar_pregunta_binaria (
            "A veces, cuando estamos tristes, podemos ser muy duros con nosotros mismos.\n\n"
            "¿En los últimos días has sentido que no eres suficiente?\n\n"
            "Puedes responder, por ejemplo: 'Sí, a veces me siento así' o 'No, no me ha pasado'."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Sí, me ha pasado",
            "No, no me ha pasado",
            "No estoy seguro"
        ]
    }


def obtener_detalle_inutilidad() -> dict:
    return {
        "estado": "detalle_inutilidad",
        "mensaje": (
            "Lamento que hayas tenido esa sensación. Gracias por compartirlo.\n\n"
            "¿En qué situaciones se te viene normalmente este pensamiento a la cabeza?"
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Cuando me equivoco",
            "Cuando me comparo",
            "Cuando estoy solo/a"
        ]
    }

def obtener_mensaje_ideacion_suicida() -> dict:
    return {
        "estado": "preguntar_ideacion_suicida",
        "mensaje": (
            "Sé que esta es una pregunta difícil, pero es importante poder hablar de ello.\n\n"
            "En las últimas dos semanas, ¿has tenido pensamientos de suicidio?\n"
            "Por ejemplo, algunas personas piensan que sería mejor no estar aquí, que la vida no merece la pena, o incluso piensan en hacerse daño.\n\n"
            "Puedes responder con sinceridad. Estoy aquí para escucharte sin juzgar."
        ),
        "modo_entrada": "sugerencias",
        "sugerencias": [
            "No entiendo la pregunta",
            "No, en ningún momento",
            "Sí, pero sin intención de hacerme daño",
            "Sí, pensé en hacerme daño, pero no tengo intención",
            "Sí, pensé en hacerme daño y tengo un plan"
        ]
    }

def obtener_cierre_alto_riesgo() -> dict:
    return {
        "estado": "cerrar_evaluación_por_riesgo_alto",
        "mensaje": (
            "Gracias por compartir algo tan importante. Lo que estás viviendo merece toda la atención y el cuidado profesional posible.\n\n"
            "Por favor, contacta de inmediato con alguno de estos recursos:\n"
            "- 📞 024 (Atención al suicidio - Cruz Roja)\n"
            "- 📞 717 00 37 17 (Teléfono de la esperanza)\n"
            "- 📞 112 (Emergencias)\n\n"
            "Este asistente no puede ofrecer la ayuda humana que necesitas ahora. No estás solo/a. Hay personas preparadas para ayudarte.\n\n"
            "Aquí termina nuestra conversación por ahora. Cuídate mucho."
        ),
        "modo_entrada": "sugerencias",
        "sugerencias": []
    }

def obtener_mensaje_fatiga() -> dict:
    return {
        "estado": "preguntar_fatiga",
        "mensaje": destacar_pregunta_binaria (
            "¿Has notado últimamente que te falta energía o te cansas con más facilidad de lo habitual?\n\n"
            "Puedes responder con sinceridad. Estoy aquí para escucharte sin juzgar."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Sí, me siento más cansado/a",
            "No, tengo la misma energía de siempre",
            "No estoy seguro"
        ]
    }

def obtener_mensaje_sueno() -> dict:
    return {
        "estado": "preguntar_sueno",
        "mensaje": destacar_pregunta_binaria (
            "¿Has notado últimamente cambios o dificultades con tu sueño?\n\n"
            "Puedes responder con sinceridad, y si no estás seguro/a también puedes decírmelo."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Sí, he notado cambios",
            "No, duermo bien",
            "No estoy seguro"
        ]
    }

def obtener_detalle_sueno() -> dict:
    return {
        "estado": "detalle_sueno",
        "mensaje": (
            "Gracias por compartirlo. ¿Podrías contarme qué tipo de dificultades estás teniendo con el sueño?\n\n"
            "Por ejemplo:\n"
            "- Te cuesta dormirte\n"
            "- Te despiertas varias veces durante la noche\n"
            "- Estás durmiendo más o menos horas de lo habitual"
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Me cuesta dormirme",
            "Me despierto mucho",
            "Duermo menos horas",
            "Duermo más de lo habitual"
        ]
    }

def obtener_mensaje_apetito() -> dict:
    return {
        "estado": "preguntar_apetito",
        "mensaje": destacar_pregunta_binaria (
            "¿Has notado cambios en tu apetito o en la cantidad de comida que tomas?\n\n"
            "Puedes responder con sinceridad. Si no estás seguro/a, también puedes decírmelo."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Si, he tenido cambios en el apetito",
            "No he notado cambios",
            "No estoy seguro"
        ]
    }

def obtener_detalle_apetito() -> dict:
    return {
        "estado": "detalle_apetito",
        "mensaje": (
            "Gracias por contármelo. ¿Podrías explicarme qué cambios has notado en tu apetito o en tu forma de comer?\n\n"
            "Por ejemplo:\n"
            "- Tienes más hambre de lo normal\n"
            "- Tienes menos ganas de comer\n"
            "- Comes sin tener hambre\n"
            "- Te saltas comidas con frecuencia"
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Tengo más hambre de lo normal",
            "Me cuesta comer",
            "Como sin hambre",
            "Me salto comidas"
        ]
    }

def obtener_mensaje_concentracion() -> dict:
    return {
        "estado": "preguntar_concentracion",
        "mensaje": (
            "Cuando tenemos el ánimo bajo, puede ser difícil concentrarnos.\n\n"
            "¿Te ha costado enfocarte en actividades como leer, trabajar, seguir una conversación, etc.?\n"
            "Cuéntame si te ocurre y con qué actividades.\n\n"
            "Si no estás seguro/a, también puedes decírmelo."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Sí, me cuesta concentrarme",
            "No, me concentro bien",
            "No estoy seguro"
        ]
    }

def obtener_detalle_concentracion() -> dict:
    return {
        "estado": "detalle_concentracion",
        "mensaje": (
            "¿En qué situaciones sientes que te cuesta más concentrarte?\n\n"
            "Por ejemplo:\n"
            "- Al leer\n"
            "- Al mantener una conversación\n"
            "- Al trabajar o estudiar\n"
            "- Al hacer tareas cotidianas"
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Al leer",
            "Al trabajar",
            "Al hablar con gente",
            "Con tareas sencillas"
        ]
    }

def obtener_mensaje_agitacion() -> dict:
    return {
        "estado": "preguntar_agitacion",
        "mensaje": destacar_pregunta_binaria (
            "¿Has notado que últimamente sientes inquietud o agitación?\n\n"
            "Por ejemplo:\n"
            "- Sensación de no poder estar quieto\n"
            "- Moverte constantemente\n"
            "- Sentirte inquieto/a sin saber por qué\n\n"
            "Puedes contestar con sinceridad, también si no estás seguro/a."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Sí, me siento inquieto",
            "No, estoy tranquilo",
            "No estoy seguro"
        ]
    }

def obtener_detalle_agitacion() -> dict:
    return {
        "estado": "detalle_agitacion",
        "mensaje": (
            "Gracias por tu sinceridad. ¿Podrías describirme cómo sientes esa inquietud o agitación?\n\n"
            "Por ejemplo:\n"
            "- Siento una energía que no puedo controlar\n"
            "- Me muevo sin parar o no puedo relajarme\n"
            "- Tengo sensación de estar acelerado sin motivo"
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Me cuesta estar quieto",
            "Siento mucha energía en el cuerpo",
            "No consigo relajarme",
            "Estoy inquieto sin motivo"
        ]
    }

def obtener_mensaje_antecedentes_generales() -> dict:
    return {
        "estado": "preguntar_antecedentes_generales",
        "mensaje": (
            "Cuando sientes tristeza, ¿hay algo que suela desencadenarla?\n\n"
            "Por ejemplo:\n"
            "- Situaciones específicas\n"
            "- Pensamientos recurrentes\n"
            "- Ciertas preocupaciones o recuerdos\n\n"
            "Cuéntame lo que sueles notar antes de sentirte así."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Me afectan ciertas situaciones familiares",
            "Los pensamientos negativos me hacen sentir triste",
            "Me preocupa mucho el futuro",
            "No lo tengo claro, pero creo que algunas cosas lo provocan"
        ]
    }

def obtener_mensaje_consecuentes_generales_1() -> dict:
    return {
        "estado": "preguntar_consecuentes_generales_1",
        "mensaje": (
            "Cuando sientes tristeza, ¿qué sueles hacer?\n\n"
            "Por ejemplo, hay personas que llaman a un familiar, otras comen algo dulce, etc. Cuéntame con detalle qué haces tú."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Llamo a un familiar o amigo",
            "Me encierro en mi habitación",
            "Como algo dulce o salado",
            "No suelo hacer nada en particular"
        ]
    }

def obtener_mensaje_consecuentes_generales_2() -> dict:
    return {
        "estado": "preguntar_consecuentes_generales_2",
        "mensaje": (
            "¿Has notado cambios en tu comportamiento cuando sientes tristeza?\n\n"
            "Por ejemplo, evitar situaciones sociales, dejar de hacer ciertas actividades, etc. Cuéntame con detalle qué cambios has notado."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Evito salir de casa",
            "No hablo con nadie",
            "He dejado de hacer cosas que me gustaban",
            "No he notado cambios"
        ]
    }

def obtener_mensaje_impacto_diario() -> dict:
    return {
        "estado": "preguntar_impacto_diario",
        "mensaje": (
            "¿Dirías que estos sentimientos han afectado tu vida diaria? Por ejemplo, en el trabajo, estudios, relaciones sociales o bienestar personal."
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Sí, ha afectado mi vida diaria",
            "No, no ha afectado mi vida diaria",
            "No estoy seguro"
        ]
    }

def obtener_detalle_impacto_diario() -> dict:
    return {
        "estado": "detalle_impacto_diario",
        "mensaje": (
            "¿Podrías contarme en qué aspectos de tu vida diaria sientes más dificultades debido a estos sentimientos?\n\n"
            "Por ejemplo:\n"
            "- Te cuesta concentrarte en el trabajo o estudios\n"
            "- Evitas reuniones sociales o familiares\n"
            "- Descuidas tu autocuidado o bienestar personal"
        ),
        "modo_entrada": "mixto",
        "sugerencias": [
            "Me cuesta rendir en el trabajo",
            "Evito a otras personas",
            "Descuido mi bienestar",
            "Me cuesta seguir rutinas"
        ]
    }

def obtener_mensaje_estrategias_1() -> dict:
    return {
        "estado": "preguntar_estrategias_1",
        "mensaje": "¿Qué cosas sueles hacer para lidiar con la tristeza?",
        "modo_entrada": "mixto",
        "sugerencias": [
            "Hablo con un amigo",
            "Salgo a caminar",
            "Escucho música",
            "Escribo lo que siento"
        ]
    }

def obtener_mensaje_estrategias_2() -> dict:
    return {
        "estado": "preguntar_estrategias_2",
        "mensaje": "¿Existen actividades o estrategias que te ayuden a sentirte mejor cuando sientes tristeza?",
        "modo_entrada": "mixto",
        "sugerencias": [
            "Hago ejercicio",
            "Practico relajación",
            "Veo una película",
            "Medito"
        ]
    }

def obtener_mensaje_cierre(nombre_usuario: str) -> dict:
    return {
        "estado": "cierre_conversacion",
        "mensaje": (
            f"Muchas gracias {nombre_usuario} por compartir cómo te has sentido últimamente.\n\n"
            "Si sientes que el bajo estado de ánimo interfiere en tu vida diaria, hablar con un profesional puede ayudarte a encontrar "
            "estrategias eficaces para manejarlo.\n\n"
            "Puedes presentarle el informe que se genera a continuación para agilizar su trabajo."
        ),
        "modo_entrada": "ninguno",
        "sugerencias": []
    }

def obtener_mensaje_percepcion_empatia() -> dict:
    return {
        "estado": "preguntar_percepcion_empatia",
        "mensaje": (
            "Antes de finalizar, me gustaría preguntarte cómo te has sentido con esta evaluación.\n\n"
            "En una escala del 0 al 10, donde:\n"
            "- 0 significa que el chatbot no fue nada empático\n"
            "- 10 significa que fue completamente empático\n\n"
            "¿Cómo calificarías la empatía del chatbot?"
        ),
        "modo_entrada": "sugerencias",
        "sugerencias": [str(i) for i in range(0, 11)]
    }


def obtener_mensaje_esperar_siguiente_pregunta() -> dict:
    return {
        "estado": "esperar_siguiente_pregunta",
        "mensaje": "",
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }
