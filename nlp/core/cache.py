# Importamos librerías necesarias
import redis
import hashlib
import json
import os
from typing import Optional

# Configuración de conexión a Redis con variables de entorno
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    # Intentamos conectar con Redis
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    redis_client.ping()  # Verificamos que la conexión funciona
except redis.exceptions.ConnectionError:
    # Si falla la conexión, desactivamos la caché
    redis_client = None
    print("Aviso: No se pudo conectar a Redis. La caché estará deshabilitada.")

# Función para consultar la caché
def obtener_cache(texto: str) -> Optional[dict]:
    """
    Devuelve la respuesta almacenada en caché para el texto dado, si existe.
    """
    if not redis_client:
        return None
    # Usamos SHA-256 para generar una clave única a partir del texto
    clave = hashlib.sha256(texto.encode()).hexdigest()
    respuesta = redis_client.get(clave)
    # Si hay respuesta, la convertimos de JSON a diccionario
    return json.loads(respuesta) if respuesta else None

# Función para guardar una respuesta en la caché
def guardar_cache(texto: str, resultado: dict, expiracion_segundos: int = 3600):
    """
    Guarda el resultado asociado al texto, con expiración por defecto de 1 hora.
    """
    if not redis_client:
        return
    clave = hashlib.sha256(texto.encode()).hexdigest()
    redis_client.set(clave, json.dumps(resultado), ex=expiracion_segundos)
