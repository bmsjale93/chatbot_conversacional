import redis
import os
import json

# Configuración de Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
except redis.exceptions.ConnectionError:
    redis_client = None
    print("⚠️ Redis no disponible. Puntuaciones no serán almacenadas.")

# -------------------- Diccionarios de puntuación --------------------

FRECUENCIA_MAP = {
    "todos los días": 3,
    "casi todos los días": 3,
    "a menudo": 2,
    "de vez en cuando": 2,
    "rara vez": 1,
}

DURACION_MAP = {
    "semanas": 3,
    "días": 2,
    "horas": 1,
    "un par de horas": 1,
    "unas horas": 1,
}


# -------------------- Funciones de cálculo --------------------

def calcular_puntuacion(tipo: str, valor: str) -> int:
    valor = valor.strip().lower()
    if tipo == "frecuencia":
        return FRECUENCIA_MAP.get(valor, 1)
    elif tipo == "duracion":
        return DURACION_MAP.get(valor, 1)
    elif tipo == "intensidad":
        try:
            n = int(valor)
            return 1 if n <= 3 else 2 if n <= 7 else 3
        except ValueError:
            return 1
    return 0


# -------------------- Gestión de puntuaciones --------------------

def obtener_puntuaciones(session_id: str) -> dict:
    if not redis_client:
        return {}
    key = f"puntuacion_usuario:{session_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else {}


def asignar_puntuacion(session_id: str, tipo: str, valor: str):
    if not redis_client:
        return

    key = f"puntuacion_usuario:{session_id}"
    puntuaciones = obtener_puntuaciones(session_id)
    puntos = calcular_puntuacion(tipo, valor)

    puntuaciones[tipo] = puntos
    puntuaciones["total"] = sum(
        v for k, v in puntuaciones.items() if k != "total"
    )

    redis_client.set(key, json.dumps(puntuaciones), ex=3600)


def eliminar_puntuaciones(session_id: str):
    if redis_client:
        redis_client.delete(f"puntuacion_usuario:{session_id}")


def generar_resumen_evaluacion(session_id: str) -> dict:
    puntuaciones = obtener_puntuaciones(session_id)
    total = puntuaciones.get("total", 0)

    if total <= 3:
        evaluacion = "leve"
    elif total <= 6:
        evaluacion = "moderado"
    else:
        evaluacion = "grave"

    return {
        "perfil_emocional": puntuaciones,
        "evaluacion": evaluacion
    }
