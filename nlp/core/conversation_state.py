import redis
import os
import json
from typing import Optional

# Configuración de Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Inicializamos cliente Redis
try:
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
except redis.exceptions.ConnectionError:
    redis_client = None
    print("⚠️ No se pudo conectar a Redis. El sistema de estados estará desactivado.")

# ---------------------------- FUNCIONES DE ESTADO ----------------------------


def obtener_estado_usuario(session_id: str) -> Optional[dict]:
    """
    Recupera el estado conversacional actual de un usuario.
    
    Args:
        session_id: ID único de la sesión del usuario.

    Returns:
        Diccionario con el estado actual o None si no existe.
    """
    if not redis_client:
        return None

    datos = redis_client.get(f"estado_usuario:{session_id}")
    return json.loads(datos) if datos else None


def guardar_estado_usuario(session_id: str, data: dict) -> None:
    """
    Guarda o actualiza el estado conversacional del usuario.

    Args:
        session_id: ID único de la sesión del usuario.
        data: Diccionario con los datos a guardar.
    """
    if not redis_client:
        return

    redis_client.set(f"estado_usuario:{session_id}", json.dumps(
        data), ex=3600)  # 1 hora de expiración


def actualizar_estado_usuario(session_id: str, nuevo_estado: str) -> None:
    """
    Cambia únicamente el campo 'estado_actual' del usuario.

    Args:
        session_id: ID único de la sesión.
        nuevo_estado: Nuevo estado conversacional a establecer.
    """
    if not redis_client:
        return

    estado = obtener_estado_usuario(session_id)
    if estado is None:
        estado = {}

    estado["estado_actual"] = nuevo_estado
    guardar_estado_usuario(session_id, estado)


def borrar_estado_usuario(session_id: str) -> None:
    """
    Elimina completamente el estado del usuario (por ejemplo, al terminar conversación).

    Args:
        session_id: ID único de la sesión.
    """
    if not redis_client:
        return

    redis_client.delete(f"estado_usuario:{session_id}")
# -----------------------------------------------------------------------------
