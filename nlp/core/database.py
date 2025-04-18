from pymongo import MongoClient
from datetime import datetime
import os
from core.security import anonimizar_texto

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
        "emocion": emocion,
        "timestamp": datetime.utcnow()
    }
    if guardar_texto_original:
        doc["mensaje_usuario"] = texto  # Útil solo para tests o debugging
    conversaciones.insert_one(doc)


def guardar_interaccion_completa(session_id: str, estado: str, pregunta: str, respuesta_usuario: str, emocion: str, puntuacion: int):
    doc = {
        "session_id": session_id,
        "estado": estado,
        "pregunta": pregunta,
        "respuesta_usuario": respuesta_usuario,
        "emocion": emocion,
        "puntuacion": puntuacion,
        "timestamp": datetime.utcnow()
    }
    conversaciones.insert_one(doc)