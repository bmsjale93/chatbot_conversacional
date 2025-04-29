import re
import unicodedata
from typing import Optional

# -------------------- Expresiones Regulares --------------------
PATRON_URL = re.compile(r"http\S+")
PATRON_NO_ALFANUMERICO = re.compile(r"[^a-záéíóúñü0-9\s]", re.IGNORECASE)
PATRON_MULTIPLES_ESPACIOS = re.compile(r"\s+")

# -------------------- Función Principal --------------------
def limpiar_texto(texto: Optional[str]) -> str:
    """
    Limpia un texto eliminando URLs, caracteres no alfabéticos, puntuación y espacios innecesarios.
    
    Args:
        texto (str | None): Texto original a limpiar.

    Returns:
        str: Texto limpio y normalizado.
    """
    if not texto or not isinstance(texto, str):
        return ""

    # Normalización unicode para tratar tildes y caracteres especiales de forma consistente
    texto = unicodedata.normalize("NFC", texto)

    texto = texto.lower()                         # Todo a minúsculas
    texto = PATRON_URL.sub("", texto)             # Eliminar URLs
    texto = PATRON_NO_ALFANUMERICO.sub("", texto)  # Eliminar símbolos raros
    texto = PATRON_MULTIPLES_ESPACIOS.sub(" ", texto)  # Unificar espacios

    return texto.strip()  # Quitar espacios extremos
