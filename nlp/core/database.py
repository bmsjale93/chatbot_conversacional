from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime, timezone
from typing import Optional
import os
import logging

from core.security import anonimizar_texto
from core.emotion_model import analizar_sentimiento
from core.score_manager import obtener_puntuaciones

# Configuración del logger
logger = logging.getLogger(__name__)

# Conexión a MongoDB
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
cliente = MongoClient(MONGO_URL)
db = cliente.get_database("chatbot")
conversaciones = db.get_collection("historial")

# ------------------------ FUNCIONES PRINCIPALES ------------------------

def guardar_interaccion(
    texto: str,
    respuesta: str,
    emocion: str,
    guardar_texto_original: bool = False
) -> None:
    doc = {
        "mensaje_hash": anonimizar_texto(texto),
        "respuesta_sistema": respuesta,
        "emocion": emocion.lower(),
        "timestamp": datetime.now(timezone.utc)
    }

    if guardar_texto_original:
        doc["mensaje_usuario"] = texto

    try:
        conversaciones.insert_one(doc)
    except PyMongoError as e:
        logger.error(f"❌ Error guardando interacción (simple): {e}")


def guardar_interaccion_completa(
    session_id: str,
    estado: str,
    pregunta: str,
    respuesta_usuario: str
) -> None:
    emocion_detectada = analizar_sentimiento(respuesta_usuario).get(
        "estado_emocional", "pendiente").lower()
    
    # Extraer la puntuación específica según el estado
    puntuaciones = obtener_puntuaciones(session_id)
    tipo = None
    if estado == "preguntar_frecuencia":
        tipo = "frecuencia"
    elif estado == "preguntar_duracion":
        tipo = "duracion"
    elif estado == "intensidad_tristeza":
        tipo = "intensidad"

    puntuacion = puntuaciones.get(tipo, 0) if tipo else 0

    doc = {
        "session_id": session_id,
        "estado": estado,
        "pregunta": pregunta,
        "respuesta_usuario": respuesta_usuario,
        "emocion": emocion_detectada,
        "puntuacion": puntuacion,
        "timestamp": datetime.now(timezone.utc)
    }

    try:
        conversaciones.insert_one(doc)
    except PyMongoError as e:
        logger.error(f"❌ Error guardando interacción completa: {e}")
