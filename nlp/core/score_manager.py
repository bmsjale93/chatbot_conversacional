import redis
import os
import json
import re
from typing import Optional
from core.cleaner import limpiar_texto

# -------------------- Configuración de Redis --------------------

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
except redis.exceptions.ConnectionError:
    redis_client = None
    print("⚠️ Redis no disponible. Puntuaciones no serán almacenadas.")

# -------------------- Diccionarios de patrones --------------------

FRECUENCIA_PATRONES = {
    9: [
        "todos los días", "cada día", "diariamente", "a diario", "casi todos los días",
        "día tras día", "sin falta", "todos los santos días"
    ],
    6: [
        "muy seguido", "a menudo", "frecuentemente", "varias veces por semana",
        "de vez en cuando", "ocasionalmente", "algunas veces", "algunos días",
        "bastantes días", "la mayoría de los días", "con frecuencia", "muchos días"
    ],
    3: [
        "rara vez", "pocas veces", "casi nunca", "nunca", "muy pocas veces",
        "alguna vez", "en contadas ocasiones"
    ]
}

DURACION_PATRONES = {
    9: [
        "semanas", "una semana", "más de una semana", "muchos días",
        "varias semanas", "largos periodos", "mucho tiempo", "durante semanas"
    ],
    6: [
        "días", "varios días", "uno o dos días", "algunos días",
        "un par de días", "durante días"
    ],
    3: [
        "horas", "un par de horas", "unas horas", "minutos", "media hora",
        "rato", "corto tiempo", "instantes", "momentos", "breve"
    ]
}

# -------------------- Funciones de cálculo --------------------

def buscar_valor_aproximado(valor_usuario: str, patrones: dict) -> int:
    valor_usuario = valor_usuario.lower().strip()
    for puntuacion, expresiones in patrones.items():
        for expresion in expresiones:
            if expresion in valor_usuario:
                return puntuacion
    return 3  # Por defecto

def calcular_puntuacion(tipo: str, valor: str) -> int:
    valor_normalizado = limpiar_texto(valor.lower().strip())

    if tipo == "intensidad":
        coincidencias = re.findall(r"\b([1-9]|10)\b", valor_normalizado)
        if coincidencias:
            n = int(coincidencias[0])
            return 9 if n >= 8 else 6 if n >= 4 else 3
        return 3

    elif tipo == "frecuencia":
        return buscar_valor_aproximado(valor_normalizado, FRECUENCIA_PATRONES)

    elif tipo == "duracion":
        return buscar_valor_aproximado(valor_normalizado, DURACION_PATRONES)

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
