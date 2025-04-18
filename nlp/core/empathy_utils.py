from typing import Optional

# Palabras clave consideradas ambiguas
RESPUESTAS_AMBIGUAS = [
    "no sé", "no lo sé", "no estoy seguro", "quizás", "tal vez",
    "puede ser", "no entiendo", "no sé qué decir", "npi", "ni idea"
]


def detectar_ambiguedad(texto: str) -> bool:
    """Devuelve True si el texto se considera una respuesta ambigua."""
    texto = texto.strip().lower()
    return any(ambigua in texto for ambigua in RESPUESTAS_AMBIGUAS)


def generar_respuesta_aclaratoria(estado_actual: str) -> dict:
    """Genera una respuesta para pedir aclaración y mantener el mismo estado."""
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
    """Agrega una frase empática al inicio del mensaje base según el tipo emocional."""
    frases = {
        "tristeza": "Lamento que te sientas así, compartirlo ya es un primer paso importante. ",
        "ansiedad": "Entiendo que puede ser difícil hablar de esto. ",
        "enojo": "Gracias por expresar cómo te sientes. ",
    }
    frase_empatica = frases.get(tipo, "")
    return f"{frase_empatica}{mensaje_base}"
