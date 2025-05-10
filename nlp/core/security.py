import hashlib

def anonimizar_texto(texto: str) -> str:
    """
    Anonimiza un texto utilizando un hash SHA-256 tras normalizarlo.
    """
    if not texto.strip():
        raise ValueError("El texto a anonimizar no puede estar vacío o contener solo espacios.")

    texto_normalizado = texto.strip().lower()
    return hashlib.sha256(texto_normalizado.encode("utf-8")).hexdigest()