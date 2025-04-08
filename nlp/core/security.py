# Importamos hashlib para generar hashes
import hashlib

# Función para anonimizar un texto usando SHA-256
def anonimizar_texto(texto: str) -> str:
    """
    Devuelve un hash SHA-256 del texto original para asegurar la anonimización.
    """
    if not texto:
        # Lanzamos error si el texto está vacío
        raise ValueError("El texto a anonimizar no puede estar vacío.")

    # Normalizamos el texto (eliminamos espacios y pasamos a minúsculas)
    texto_normalizado = texto.strip().lower()
    # Generamos y devolvemos el hash
    return hashlib.sha256(texto_normalizado.encode('utf-8')).hexdigest()
