import re
import unicodedata
from typing import Optional

# -------------------- Expresiones Regulares --------------------
PATRON_URL = re.compile(r"http\S+")
PATRON_NO_ALFANUMERICO = re.compile(r"[^a-z0-9\s]", re.IGNORECASE)
PATRON_MULTIPLES_ESPACIOS = re.compile(r"\s+")

# -------------------- Función Principal --------------------
def limpiar_texto(texto: Optional[str]) -> str:
    """
    Limpia un texto eliminando URLs, tildes, puntuación y espacios innecesarios.

    Args:
        texto (str | None): Texto original a limpiar.

    Returns:
        str: Texto limpio y normalizado.
    """
    if not isinstance(texto, str) or not texto.strip():
        return ""

    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")  # Elimina tildes

    texto = PATRON_URL.sub("", texto)               # Eliminar URLs
    texto = PATRON_NO_ALFANUMERICO.sub("", texto)   # Eliminar símbolos raros y signos
    texto = PATRON_MULTIPLES_ESPACIOS.sub(" ", texto)

    return texto.strip()
