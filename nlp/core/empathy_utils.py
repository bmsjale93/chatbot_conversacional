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

    # 1. Coincidencia exacta
    if texto_original in RESPUESTAS_AMBIGUAS:
        return True

    # 2. Patrones amplios con expresiones comunes
    if any(p.search(texto_original) for p in PATRONES_AMBIGUOS):
        return True

    # 3. Tokens de procesamiento lematizado
    texto_limpio = limpiar_texto(texto_original)
    tokens = preprocesar_texto(texto_limpio)
    if any(token in PALABRAS_CLAVE_AMBIGUAS for token in tokens):
        return True

    return False

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
        "positivo": "¡Qué bueno que te sientas bien! ",
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
