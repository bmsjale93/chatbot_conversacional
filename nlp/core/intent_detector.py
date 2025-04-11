# Palabras clave para respuestas afirmativas
PALABRAS_AFIRMATIVAS = [
    "sí", "claro", "por supuesto", "vale", "de acuerdo", "correcto", "acepto"
]

# Palabras clave para respuestas negativas
PALABRAS_NEGATIVAS = [
    "no", "prefiero no", "rechazo", "nunca", "no quiero", "no deseo"
]


def detectar_intencion(texto_limpio: str) -> str:
    """
    Analiza el texto procesado y devuelve:
    - 'afirmativo' si detecta respuesta positiva.
    - 'negativo' si detecta respuesta negativa.
    - 'desconocido' si no puede decidir.
    """

    texto = texto_limpio.lower()

    for palabra in PALABRAS_AFIRMATIVAS:
        if palabra in texto:
            return "afirmativo"

    for palabra in PALABRAS_NEGATIVAS:
        if palabra in texto:
            return "negativo"

    return "desconocido"