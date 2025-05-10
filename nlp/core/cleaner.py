import re
import unicodedata
from typing import Optional

# -------- Patrones regulares para limpieza --------
PATRON_URL = re.compile(r"http\S+")
PATRON_NO_ALFANUMERICO = re.compile(r"[^a-z0-9\s]", re.IGNORECASE)
PATRON_MULTIPLES_ESPACIOS = re.compile(r"\s+")

def limpiar_texto(texto: Optional[str]) -> str:
    """
    Normaliza un texto eliminando URLs, tildes, caracteres no alfanuméricos y espacios innecesarios.
    """
    if not isinstance(texto, str) or not texto.strip():
        return ""

    # Pasar a minúsculas y eliminar tildes
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")

    # Aplicar limpieza con expresiones regulares
    texto = PATRON_URL.sub("", texto)
    texto = PATRON_NO_ALFANUMERICO.sub("", texto)
    texto = PATRON_MULTIPLES_ESPACIOS.sub(" ", texto)

    return texto.strip()
