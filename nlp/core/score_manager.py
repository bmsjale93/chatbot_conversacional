import redis
import os
import json
from core.cleaner import limpiar_texto

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

# -------------------- Diccionarios de puntuación extendidos --------------------

FRECUENCIA_PATRONES = {
    3: [
        "todos los días", "cada día", "diariamente", "a diario", "casi todos los días",
        "día tras día", "sin falta", "todos los santos días"
    ],
    2: [
        "muy seguido", "a menudo", "frecuentemente", "varias veces por semana",
        "de vez en cuando", "ocasionalmente", "algunas veces", "algunos días",
        "bastantes días", "la mayoría de los días", "con frecuencia", "muchos días"
    ],
    1: [
        "rara vez", "pocas veces", "casi nunca", "nunca", "muy pocas veces",
        "alguna vez", "en contadas ocasiones"
    ]
}


DURACION_PATRONES = {
    3: [
        "semanas", "una semana", "más de una semana", "muchos días",
        "varias semanas", "largos periodos", "mucho tiempo", "durante semanas"
    ],
    2: [
        "días", "varios días", "uno o dos días", "algunos días",
        "un par de días", "durante días"
    ],
    1: [
        "horas", "un par de horas", "unas horas", "minutos", "media hora",
        "rato", "corto tiempo", "instantes", "momentos", "breve"
    ]
}


# -------------------- Funciones de cálculo --------------------

def buscar_valor_aproximado(valor_usuario: str, patrones: dict) -> int:
    for puntuacion, expresiones in patrones.items():
        for expresion in expresiones:
            if expresion in valor_usuario:
                return puntuacion
    return 1

def calcular_puntuacion(tipo: str, valor: str) -> int:
    valor_limpio = limpiar_texto(valor)

    if tipo == "frecuencia":
        return buscar_valor_aproximado(valor_limpio, FRECUENCIA_PATRONES)
    elif tipo == "duracion":
        return buscar_valor_aproximado(valor_limpio, DURACION_PATRONES)
    elif tipo == "intensidad":
        try:
            n = int(valor.strip())
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
