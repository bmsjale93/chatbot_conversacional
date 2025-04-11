from pymongo import MongoClient
from datetime import datetime
import os
from core.security import anonimizar_texto

MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
cliente = MongoClient(MONGO_URL)
db = cliente.chatbot
conversaciones = db.historial


def guardar_interaccion(texto: str, respuesta: str, emocion: str, guardar_texto_original: bool = False):
    """
    Guarda en la base de datos el mensaje del usuario, la respuesta del sistema y la emoción detectada.
    El mensaje se guarda de forma anonimizada para proteger la privacidad.
    Opcionalmente guarda también el texto original si se necesita para pruebas.
    """
    doc = {
        "mensaje_hash": anonimizar_texto(texto),
        "respuesta_sistema": respuesta,
        "emocion": emocion,
        "timestamp": datetime.utcnow()
    }
    if guardar_texto_original:
        doc["mensaje_usuario"] = texto  # Solo en entornos de test

    conversaciones.insert_one(doc)
