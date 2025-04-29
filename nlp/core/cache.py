import redis
import hashlib
import json
import os
from typing import Optional, Any

# -------------------- Configuración --------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    cache_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    cache_client.ping()
except redis.exceptions.ConnectionError:
    cache_client = None
    print("⚠️ Aviso: No se pudo conectar a Redis. La caché estará deshabilitada.")

# -------------------- Utilidades --------------------
def generar_clave_cache(texto: str) -> str:
    """Genera un hash SHA-256 del texto para usar como clave única en la caché."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

# -------------------- Operaciones de Caché --------------------
def obtener_cache(texto: str) -> Optional[dict[str, Any]]:
    """
    Recupera una respuesta previamente almacenada en caché para un texto dado.

    Args:
        texto (str): Texto original del mensaje.

    Returns:
        dict o None: La respuesta almacenada, o None si no existe o hay error.
    """
    if not cache_client:
        return None
    try:
        clave = generar_clave_cache(texto)
        resultado = cache_client.get(clave)
        return json.loads(resultado) if resultado else None
    except Exception as e:
        print(f"⚠️ Error al obtener desde caché: {e}")
        return None


def guardar_cache(texto: str, resultado: dict, expiracion_segundos: int = 3600) -> None:
    """
    Almacena una respuesta en la caché, asociada al texto original.

    Args:
        texto (str): Texto original del mensaje.
        resultado (dict): Respuesta a guardar.
        expiracion_segundos (int): Tiempo de expiración en segundos (por defecto 1 hora).
    """
    if not cache_client:
        return
    try:
        clave = generar_clave_cache(texto)
        cache_client.set(clave, json.dumps(resultado), ex=expiracion_segundos)
    except Exception as e:
        print(f"⚠️ Error al guardar en caché: {e}")
