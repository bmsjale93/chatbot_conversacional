from typing import Optional, Dict
from core.cleaner import limpiar_texto
from core.processor import preprocesar_texto
import re

# -------------------- Ambigüedad general --------------------

RESPUESTAS_AMBIGUAS = {
    "no sé", "no lo sé", "no lo se", "no estoy seguro", "no estoy segura", "quizás", "tal vez",
    "puede ser", "no entiendo", "no sé qué decir", "npi", "ni idea", "no sabría decir",
    "dudo", "estoy confundido", "no me queda claro", "no tengo claro", "no puedo responder",
    "creo que sí pero no sé", "no sé exactamente", "difícil de decir", "es complicado"
}

PALABRAS_CLAVE_AMBIGUAS = {
    "dudo", "confuso", "indeciso", "inseguro", "quizás", "tal", "vez",
    "complicado", "difícil", "ambigua", "ambigüedad", "confundido", "confundida"
}

PATRONES_AMBIGUOS = [
    re.compile(r"\bno\s+(lo\s+)?sé\b", re.IGNORECASE),
    re.compile(r"\bno\s+estoy\s+(seguro|segura)\b", re.IGNORECASE),
    re.compile(r"\bquizás\b", re.IGNORECASE),
    re.compile(r"\btal\s+vez\b", re.IGNORECASE),
    re.compile(r"\bpuede\s+ser\b", re.IGNORECASE),
    re.compile(r"\bni\s+idea\b", re.IGNORECASE),
    re.compile(r"\bno\s+entiendo\b", re.IGNORECASE),
    re.compile(r"\bno\s+sabría\s+decir\b", re.IGNORECASE),
    re.compile(r"\bno\s+(me\s+)?queda\s+claro\b", re.IGNORECASE),
    re.compile(r"\bes\s+complicado\b", re.IGNORECASE),
    re.compile(r"\bdifícil\s+de\s+decir\b", re.IGNORECASE),
]

def detectar_ambiguedad(texto: Optional[str]) -> bool:
    """
    Devuelve True si el texto se considera una respuesta ambigua.
    """
    if not texto:
        return True

    texto_original = texto.strip().lower()

    if texto_original in RESPUESTAS_AMBIGUAS:
        return True

    if any(p.search(texto_original) for p in PATRONES_AMBIGUOS):
        return True

    texto_limpio = limpiar_texto(texto_original)
    tokens = preprocesar_texto(texto_limpio)
    return any(token in PALABRAS_CLAVE_AMBIGUAS for token in tokens)

# -------------------- Mensajes de aclaración --------------------

def generar_respuesta_aclaratoria(estado_actual: str) -> Dict[str, str]:
    """
    Genera una respuesta para pedir aclaración al usuario manteniendo el mismo estado,
    adaptando el mensaje según el contexto del estado actual.
    """
    if estado_actual == "preguntar_identidad":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no sabes cómo describirte aún, pero si puedes, indícame una etiqueta con la que te identifiques "
                "(por ejemplo: Masculino, Femenino o No binario). Esto me ayudará a personalizar mejor la conversación."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Masculino", "Femenino", "No binario"]
        }

    if estado_actual == "inicio_exploracion_tristeza":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no lo tienes del todo claro. A veces identificar cómo nos sentimos puede resultar confuso.\n\n"
                "Me gustaría saber si en los últimos días has experimentado algún momento de tristeza, malestar emocional o sensación de bajón. "
                "No importa si fue algo breve o si no estás seguro de cómo describirlo.\n\n"
                "¿Dirías que has pasado por algo así recientemente?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Sí, me he sentido triste", "No, me he sentido bien", "No estoy seguro"]
        }

    if estado_actual == "preguntar_frecuencia":
        return {
            "estado": estado_actual,
            "mensaje": (
                "No te preocupes si no puedes dar una respuesta exacta.\n\n"
                "Cuando te preguntaba por la frecuencia con la que sientes tristeza, me refería a si ocurre todos los días, algunas veces por semana, "
                "solo ocasionalmente o muy rara vez.\n\n"
                "¿Cómo describirías la frecuencia con la que sientes tristeza últimamente?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Todos los días", "A menudo", "De vez en cuando", "Rara vez"]
        }

    if estado_actual == "preguntar_duracion":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Gracias por compartirlo. Sé que a veces puede ser difícil precisar exactamente cuánto tiempo dura la tristeza.\n\n"
                "Solo necesito una idea general: ¿suele durar unos minutos, unas horas, varios días o incluso semanas?\n\n"
                "Puedes responder, por ejemplo: 'Unas horas', 'Dos días', 'Semanas', etc."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Unas horas", "Dos días", "Semanas"]
        }

    if estado_actual == "intensidad_tristeza":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Entiendo que a veces puede ser complicado ponerle un número exacto a lo que sentimos.\n\n"
                "Solo necesito una idea general de cuán intensa es tu tristeza cuando aparece. "
                "Puedes indicarlo usando una escala del 1 (muy leve) al 10 (muy intensa), o algo aproximado como: "
                "'Creo que un 4' o 'más o menos un 7'."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["1", "5", "10"]
        }
    
    if estado_actual == "preguntar_empatia":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no tienes un número exacto ahora mismo.\n\n"
                "¿Podrías indicarme aproximadamente cómo te has sentido durante esta conversación conmigo?\n"
                "Utiliza una escala del 0 (nada empático) al 10 (muy empático), o una expresión como:\n"
                "'Más o menos un 6', 'Creo que un 7', 'Entre 4 y 5'."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["3", "6", "10"]
        }
    
    if estado_actual == "preguntar_anhedonia":
        return {
            "estado": estado_actual,
            "mensaje": (
                "No pasa nada si no estás seguro/a. Me refiero a si últimamente has dejado de disfrutar cosas que antes te gustaban, "
                "como ver una película, estar con amigos, leer, hacer deporte o cualquier otra actividad que solías disfrutar.\n\n"
                "¿Dirías que has notado esa pérdida de interés o placer?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Sí, he perdido interés", "No, sigo disfrutando igual", "No lo sé"]
        }

    if estado_actual == "preguntar_desesperanza":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no lo tienes claro. A veces cuesta poner en palabras cómo nos sentimos con respecto al futuro.\n\n"
                "Cuando te pregunto si te cuesta encontrar algo que te motive o ilusione, me refiero a si ves difícil entusiasmarte con cosas por venir, ya sean planes, metas o actividades.\n\n"
                "¿Te sientes así últimamente?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Sí, me cuesta ilusionarme", "No, tengo metas", "No estoy seguro"]
        }


    return {
        "estado": estado_actual,
        "mensaje": (
            "Permíteme explicarlo de otra forma. No te preocupes si no tienes una respuesta clara aún, "
            "puedes tomarte tu tiempo para pensarla o decir lo primero que te venga a la mente."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }
# -------------------- Mensajes empáticos --------------------

def generar_respuesta_empatica(mensaje_base: str, tipo: str = "tristeza") -> str:
    """
    Agrega una frase empática al inicio del mensaje base según el tipo emocional.
    """
    frases_empaticas = {
        "tristeza": "Lamento que te sientas así, compartirlo ya es un primer paso importante. ",
        "ansiedad": "Entiendo que puede ser difícil hablar de esto. ",
        "enojo": "Gracias por expresar cómo te sientes. ",
        "neutral": "Gracias por compartir cómo te sientes. ",
        "positivo": "Qué bueno que te sientas bien. ",
    }
    frase_intro = frases_empaticas.get(tipo, "")
    return f"{frase_intro}{mensaje_base}"

# -------------------- Ambigüedad específica de identidad --------------------

RESPUESTAS_AMBIGUAS_IDENTIDAD = {
    "no lo sé", "no sé", "no estoy seguro", "no quiero decirlo",
    "prefiero no decirlo", "ninguno", "ninguna", "n/a", "no binarie",
    "sin definir", "no definido", "indefinido", "sin género", "sin genero",
    "sin identidad", "no quiero responder", "no sé qué soy"
}

def detectar_ambiguedad_identidad(texto: Optional[str]) -> bool:
    """
    Devuelve True si la respuesta sobre identidad se considera ambigua.
    """
    if not texto:
        return True
    texto_limpio = limpiar_texto(texto)
    return any(ambigua in texto_limpio for ambigua in RESPUESTAS_AMBIGUAS_IDENTIDAD)
