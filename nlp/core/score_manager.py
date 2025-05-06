import redis
import os
import json
import re
from typing import Optional

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

DURACION_PATRONES = {
    10: [
        "semanas completas", "más de un mes", "varios meses", "durante mucho tiempo",
        "meses enteros", "desde hace mucho", "por un largo tiempo", "periodos prolongados",
        "varios meses seguidos"
    ],
    9: [
        "más de tres semanas", "aproximadamente un mes", "casi un mes entero", "alrededor de un mes",
        "muchísimo tiempo", "más de 21 días", "por mucho tiempo seguido", "dura un mes o más"
    ],
    8: [
        "varias semanas", "tres semanas", "largos periodos", "suele extenderse semanas",
        "dos o tres semanas", "más de dos semanas", "entre dos y tres semanas"
    ],
    7: [
        "unas tres semanas", "casi un mes", "algo más de dos semanas", "dura bastante",
        "entre 15 y 20 días", "cerca de veinte días", "alrededor de tres semanas"
    ],
    6: [
        "dos semanas", "más de una semana", "más de diez días", "10 o 12 días", "quince días",
        "semana y media", "entre una y dos semanas", "una semana larga"
    ],
    5: [
        "una semana", "entre 7 y 10 días", "siete días exactos", "suele durar una semana",
        "siete u ocho días", "una semana justa"
    ],
    4: [
        "unos días", "algunos días", "un par de días", "durante días", "cuatro o cinco días",
        "entre tres y cinco días", "dura pocos días", "tres o cuatro días", "unos cuantos días"
    ],
    3: [
        "un día", "unas 24 horas", "todo un día", "dura solo un día", "un día entero",
        "un día exacto", "solo un día"
    ],
    2: [
        "unas horas", "medio día", "pocas horas", "instantes largos", "varias horas",
        "una tarde", "una mañana", "unas cuantas horas", "dura pocas horas"
    ],
    1: [
        "minutos", "muy poco tiempo", "momentos", "breve", "instantes",
        "pasa rápido", "dura muy poco", "solo unos minutos", "algo muy breve"
    ]
}

# -------------------- Funciones de cálculo --------------------

def buscar_valor_aproximado(valor_usuario: str, patrones: dict) -> int:
    valor_usuario = valor_usuario.lower().strip()
    for puntuacion, expresiones in patrones.items():
        for expresion in expresiones:
            if expresion in valor_usuario:
                return puntuacion
    return 1  # Por defecto, la mínima puntuación

def calcular_puntuacion(tipo: str, valor: str) -> int:
    if tipo == "intensidad":
        coincidencias = re.findall(r"\b([1-9]|10)\b", valor)
        if coincidencias:
            n = int(coincidencias[0])
            return 9 if n >= 8 else 6 if n >= 4 else 3
        return 3

    elif tipo == "frecuencia":
        # No se limpia, porque se selecciona directamente de sugerencias exactas
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
        return MAPEO_FRECUENCIA.get(valor.strip(), 1)

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
        return MAPEO_DURACION.get(valor.strip(), 1)

    elif tipo == "duracion":
        return buscar_valor_aproximado(valor.lower().strip(), DURACION_PATRONES)

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
