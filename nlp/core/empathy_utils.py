from typing import Optional, Dict

# Palabras clave consideradas ambiguas
RESPUESTAS_AMBIGUAS = {
    "no sé", "no lo sé", "no estoy seguro", "quizás", "tal vez",
    "puede ser", "no entiendo", "no sé qué decir", "npi", "ni idea"
}


def detectar_ambiguedad(texto: Optional[str]) -> bool:
    """
    Devuelve True si el texto se considera una respuesta ambigua.
    """
    if not texto:
        return True  # Consideramos ausencia como ambigüedad
    texto_normalizado = texto.strip().casefold()
    return any(ambigua in texto_normalizado for ambigua in RESPUESTAS_AMBIGUAS)


def generar_respuesta_aclaratoria(estado_actual: str) -> Dict[str, str]:
    """
    Genera una respuesta para pedir aclaración al usuario manteniendo el mismo estado.
    """
    return {
        "estado": estado_actual,
        "mensaje": (
            "Permíteme explicarlo de otra forma. No te preocupes si no tienes una respuesta clara aún, "
            "puedes tomarte tu tiempo para pensarla o decir lo primero que te venga a la mente."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }


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
