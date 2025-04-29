from typing import Literal

# Palabras clave para respuestas afirmativas
PALABRAS_AFIRMATIVAS = {
    "sí", "claro", "por supuesto", "vale", "de acuerdo", "correcto", "acepto"
}

# Palabras clave para respuestas negativas
PALABRAS_NEGATIVAS = {
    "no", "prefiero no", "rechazo", "nunca", "no quiero", "no deseo"
}


def detectar_intencion(texto_limpio: str) -> Literal["afirmativo", "negativo", "desconocido"]:
    """
    Analiza el texto procesado y devuelve:
    - 'afirmativo' si detecta respuesta positiva.
    - 'negativo' si detecta respuesta negativa.
    - 'desconocido' si no puede decidir.
    """
    if not texto_limpio:
        return "desconocido"

    texto = texto_limpio.strip().casefold()

    if any(palabra in texto for palabra in PALABRAS_AFIRMATIVAS):
        return "afirmativo"

    if any(palabra in texto for palabra in PALABRAS_NEGATIVAS):
        return "negativo"

    return "desconocido"
