import redis
import hashlib
import json
import os
from typing import Optional, Any

# -------- Configuración de conexión con Redis --------
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
    print("Aviso: No se pudo conectar a Redis. La caché estará deshabilitada.")

# -------- Utilidades --------
def generar_clave_cache(texto: str) -> str:
    """
    Genera una clave única para la caché a partir del texto original usando SHA-256.
    """
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

# -------- Funciones de lectura y escritura en caché --------
def obtener_cache(texto: str) -> Optional[dict[str, Any]]:
    """
    Recupera una respuesta almacenada en la caché si existe.
    """
    if not cache_client:
        return None
    try:
        clave = generar_clave_cache(texto)
        resultado = cache_client.get(clave)
        return json.loads(resultado) if resultado else None
    except Exception as e:
        print(f"Error al obtener desde caché: {e}")
        return None

def guardar_cache(texto: str, resultado: dict, expiracion_segundos: int = 3600) -> None:
    """
    Guarda un resultado en caché para el texto dado, con una expiración opcional.
    """
    if not cache_client:
        return
    try:
        clave = generar_clave_cache(texto)
        cache_client.set(clave, json.dumps(resultado), ex=expiracion_segundos)
    except Exception as e:
        print(f"Error al guardar en caché: {e}")
