import redis
import os
import json
import logging
from typing import Optional

# Configuración del logger
logger = logging.getLogger(__name__)

# Configuración de Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PREFIX = "estado_usuario"

# Inicializamos cliente Redis
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    redis_client.ping()
except redis.exceptions.ConnectionError:
    redis_client = None
    logger.warning(
        "⚠️ No se pudo conectar a Redis. El sistema de estados estará desactivado.")

# ---------------------------- FUNCIONES DE ESTADO ----------------------------


def _get_key(session_id: str) -> str:
    """Devuelve la clave Redis correspondiente a un usuario."""
    return f"{REDIS_PREFIX}:{session_id}"


def obtener_estado_usuario(session_id: str) -> Optional[dict]:
    """
    Recupera el estado conversacional actual de un usuario.

    Args:
        session_id (str): ID de la sesión.

    Returns:
        dict | None: Estado actual o None si no existe.
    """
    if not redis_client:
        return None

    datos = redis_client.get(_get_key(session_id))
    return json.loads(datos) if datos else None


def guardar_estado_usuario(session_id: str, data: dict) -> None:
    """
    Guarda o actualiza el estado conversacional del usuario.

    Args:
        session_id (str): ID de la sesión.
        data (dict): Estado a guardar.
    """
    if not redis_client:
        return

    redis_client.set(_get_key(session_id), json.dumps(data), ex=3600)


def actualizar_estado_usuario(session_id: str, nuevo_estado: str) -> None:
    """
    Actualiza únicamente el campo 'estado_actual' en el estado del usuario.

    Args:
        session_id (str): ID de la sesión.
        nuevo_estado (str): Nuevo estado a establecer.
    """
    if not redis_client:
        return

    estado = obtener_estado_usuario(session_id) or {}
    estado["estado_actual"] = nuevo_estado
    guardar_estado_usuario(session_id, estado)


def borrar_estado_usuario(session_id: str) -> None:
    """
    Elimina el estado del usuario por completo.

    Args:
        session_id (str): ID de la sesión.
    """
    if not redis_client:
        return

    redis_client.delete(_get_key(session_id))
