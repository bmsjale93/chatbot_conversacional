from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
import logging

logger = logging.getLogger(__name__)

# Conexión a MongoDB
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
cliente = MongoClient(MONGO_URL)
db = cliente.get_database("chatbot")
conversaciones = db.get_collection("historial")

def _obtener_historial_por_sesion(session_id: str) -> list:
    """
    Devuelve el historial ordenado de mensajes para una sesión.
    """
    try:
        historial = conversaciones.find({"session_id": session_id}).sort("timestamp", 1)
        resultado = []

        for doc in historial:
            if "pregunta" in doc:
                resultado.append({"role": "assistant", "content": doc["pregunta"]})
            if "respuesta_usuario" in doc:
                resultado.append({"role": "user", "content": doc["respuesta_usuario"]})
        
        return resultado

    except PyMongoError as e:
        logger.error(f"❌ Error recuperando historial para sesión {session_id}: {e}")
        return []

def recuperar_historial(session_id: str) -> list:
    """
    Recupera el historial completo de una sesión.
    """
    return _obtener_historial_por_sesion(session_id)
