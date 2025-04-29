import hashlib


def anonimizar_texto(texto: str) -> str:
    """
    Anonimiza un texto utilizando un hash SHA-256.
    
    El proceso elimina espacios, convierte todo a minúsculas (para evitar diferencias por capitalización),
    y genera un hash irrevertible para proteger la identidad del usuario.

    Args:
        texto (str): El texto a anonimizar.

    Returns:
        str: Hash SHA-256 del texto normalizado.

    Raises:
        ValueError: Si el texto está vacío o contiene solo espacios.
    """
    if not texto.strip():
        raise ValueError(
            "El texto a anonimizar no puede estar vacío o contener solo espacios.")

    texto_normalizado = texto.strip().lower()  # Normalizamos para uniformidad
    return hashlib.sha256(texto_normalizado.encode('utf-8')).hexdigest()
