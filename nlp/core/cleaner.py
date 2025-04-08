# Módulo de expresiones regulares
import re

# Función para limpiar el texto de entrada
def limpiar_texto(texto: str) -> str:
    """
    Limpia el texto eliminando URLs, caracteres no alfabéticos, signos de puntuación,
    múltiples espacios y lo convierte todo a minúsculas.
    """
    texto = texto.lower()  # Convertimos el texto a minúsculas
    texto = re.sub(r"http\S+", "", texto)  # Eliminamos URLs
    # Eliminamos caracteres que no sean letras, números o espacios
    texto = re.sub(r"[^a-záéíóúñü0-9\s]", "", texto)
    # Reemplazamos múltiples espacios por uno solo
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()  # Eliminamos espacios al inicio y al final
