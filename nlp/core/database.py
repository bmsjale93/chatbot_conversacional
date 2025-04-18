from pymongo import MongoClient
from datetime import datetime, timezone
import os
from core.security import anonimizar_texto
from core.emotion_model import analizar_sentimiento
from core.score_manager import obtener_puntuaciones

# Conexión a MongoDB
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
cliente = MongoClient(MONGO_URL)
db = cliente.chatbot
conversaciones = db.historial


def guardar_interaccion(texto: str, respuesta: str, emocion: str, guardar_texto_original: bool = False):
    """
    Guarda una interacción sencilla (modo legado). Anonimiza el texto salvo en modo test.
    """
    doc = {
        "mensaje_hash": anonimizar_texto(texto),
        "respuesta_sistema": respuesta,
        "emocion": emocion.lower(),
        "timestamp": datetime.now(timezone.utc)
    }
    if guardar_texto_original:
        doc["mensaje_usuario"] = texto
    conversaciones.insert_one(doc)


def guardar_interaccion_completa(session_id: str, estado: str, pregunta: str, respuesta_usuario: str):
    """
    Guarda en MongoDB una interacción completa durante la conversación,
    incluyendo análisis emocional y puntuación acumulada.
    """
    emocion_detectada = analizar_sentimiento(
        respuesta_usuario).get("estado_emocional", "pendiente").lower()
    puntuacion_actual = obtener_puntuaciones(session_id).get("total", 0)

    doc = {
        "session_id": session_id,
        "estado": estado,
        "pregunta": pregunta,
        "respuesta_usuario": respuesta_usuario,
        "emocion": emocion_detectada,
        "puntuacion": puntuacion_actual,
        "timestamp": datetime.now(timezone.utc)
    }

    conversaciones.insert_one(doc)