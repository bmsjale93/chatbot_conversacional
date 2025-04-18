import redis
import os
import json

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Diccionarios de puntuación
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

def calcular_puntuacion(tipo: str, valor: str) -> int:
    valor = valor.lower()
    if tipo == "frecuencia":
        return FRECUENCIA_MAP.get(valor, 1)
    elif tipo == "duracion":
        return DURACION_MAP.get(valor, 1)
    elif tipo == "intensidad":
        try:
            n = int(valor)
            return 1 if n <= 3 else 2 if n <= 7 else 3
        except:
            return 1
    return 0

def asignar_puntuacion(session_id: str, tipo: str, valor: str):
    key = f"puntuacion_usuario:{session_id}"
    puntuaciones = obtener_puntuaciones(session_id)
    puntos = calcular_puntuacion(tipo, valor)
    puntuaciones[tipo] = puntos
    puntuaciones["total"] = sum(
        v for k, v in puntuaciones.items() if k != "total")
    redis_client.set(key, json.dumps(puntuaciones), ex=3600)

def obtener_puntuaciones(session_id: str) -> dict:
    key = f"puntuacion_usuario:{session_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else {}


def eliminar_puntuaciones(session_id: str):
    redis_client.delete(f"puntuacion_usuario:{session_id}")


def generar_resumen_evaluacion(session_id: str) -> dict:
    puntuaciones = obtener_puntuaciones(session_id)
    return {
        "perfil_emocional": puntuaciones,
        "evaluacion": "leve" if puntuaciones.get("total", 0) <= 3 else "moderado" if puntuaciones["total"] <= 6 else "grave"
    }
