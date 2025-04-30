import unicodedata
import re
from typing import Literal

# ------------------ Expresiones Extendidas ------------------

EXPRESIONES_AFIRMATIVAS = {
    "sí", "si", "claro", "vale", "de acuerdo", "afirmativo", "por supuesto", "sin duda", "perfecto",
    "genial", "está bien", "acepto", "continuar", "adelante", "vamos", "venga", "sí quiero", "seguro",
    "me parece bien", "estoy listo", "ok", "sigamos", "sí, vamos a seguir", "continúa", "quiero seguir",
    "sí, por favor", "dale"
}

EXPRESIONES_NEGATIVAS = {
    "no", "prefiero no", "mejor no", "rechazo", "no quiero", "no deseo", "no gracias", "no por ahora",
    "nunca", "no estoy seguro", "quizá no", "no quiero seguir", "no, gracias", "ahora no", "negativo", "paso"
}

# Activar para depuración
DEBUG = False

# ------------------ Preprocesamiento ------------------
def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto.lower().strip()


def tokenizar(texto: str) -> list:
    return texto.split()

# ------------------ Detección de intención ------------------
def detectar_intencion(texto_limpio: str) -> Literal["afirmativo", "negativo", "desconocido"]:
    if not texto_limpio:
        return "desconocido"

    texto_normalizado = normalizar_texto(texto_limpio)
    tokens = set(tokenizar(texto_normalizado))

    # Depuración
    if DEBUG:
        print(f"[DEBUG] Texto normalizado: {texto_normalizado}")
        print(f"[DEBUG] Tokens: {tokens}")

    # --- Paso 1: Coincidencia exacta de frase ---
    if texto_normalizado in EXPRESIONES_AFIRMATIVAS:
        return "afirmativo"
    if texto_normalizado in EXPRESIONES_NEGATIVAS:
        return "negativo"

    # --- Paso 2: Coincidencia por tokens individuales ---
    if tokens & EXPRESIONES_AFIRMATIVAS:
        return "afirmativo"
    if tokens & EXPRESIONES_NEGATIVAS:
        return "negativo"

    # --- Paso 3: Inclusión parcial de frases ---
    for expresion in EXPRESIONES_AFIRMATIVAS:
        if expresion in texto_normalizado:
            return "afirmativo"

    for expresion in EXPRESIONES_NEGATIVAS:
        if expresion in texto_normalizado:
            return "negativo"

    # --- Paso 4: Si no se reconoce ---
    return "desconocido"
