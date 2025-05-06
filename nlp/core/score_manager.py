import redis
import os
import json
from typing import Optional

# -------------------- Configuración de Redis --------------------

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
    )
    redis_client.ping()
except redis.exceptions.ConnectionError:
    redis_client = None
    print("⚠️ Redis no disponible. Puntuaciones no serán almacenadas.")


# -------------------- Funciones de cálculo --------------------

def calcular_puntuacion(tipo: str, valor: str) -> int:
    valor = valor.strip()

    if tipo == "intensidad":
        try:
            n = int(valor)
            return n if 1 <= n <= 10 else 1
        except ValueError:
            return 1

    elif tipo == "frecuencia":
        MAPEO_FRECUENCIA = {
            "Todos los días": 10,
            "Casi todos los días": 9,
            "Muy seguido": 8,
            "A menudo": 7,
            "Algunas veces por semana": 6,
            "De vez en cuando": 5,
            "Con poca frecuencia": 4,
            "Pocas veces": 3,
            "Casi nunca": 2,
            "Nunca": 1
        }
        return MAPEO_FRECUENCIA.get(valor, 1)

    elif tipo == "duracion":
        MAPEO_DURACION = {
            "Momentos puntuales": 1,
            "Unas horas": 2,
            "Más de 6 horas": 3,
            "Un día o más": 4,
            "Entre tres y cinco días": 5,
            "Una semana": 6,
            "Poco más de una semana": 7,
            "Dos semanas": 8,
            "Varias semanas": 9,
            "Un mes o más": 10
        }
        return MAPEO_DURACION.get(valor, 1)

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

    # Calcular media si están presentes al menos dos valores
    valores = [
        puntuaciones.get("frecuencia"),
        puntuaciones.get("duracion"),
        puntuaciones.get("intensidad")
    ]
    valores_validos = [v for v in valores if isinstance(v, int)]

    puntuaciones["media"] = round(sum(valores_validos) / len(valores_validos), 2) if valores_validos else 0

    redis_client.set(key, json.dumps(puntuaciones), ex=3600)

def eliminar_puntuaciones(session_id: str):
    if redis_client:
        redis_client.delete(f"puntuacion_usuario:{session_id}")

def generar_resumen_evaluacion(session_id: str) -> dict:
    puntuaciones = obtener_puntuaciones(session_id)
    media = puntuaciones.get("media", 0)

    if media <= 3.5:
        evaluacion = "leve"
    elif media <= 6.5:
        evaluacion = "moderado"
    else:
        evaluacion = "grave"

    return {
        "perfil_emocional": puntuaciones,
        "evaluacion": evaluacion
    }
