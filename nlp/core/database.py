# Importamos MongoClient para conectarnos a MongoDB
from pymongo import MongoClient
from datetime import datetime
import os
from core.security import anonimizar_texto

# Obtenemos la URL de la base de datos desde las variables de entorno
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
# Creamos un cliente de MongoDB
cliente = MongoClient(MONGO_URL)
# Seleccionamos la base de datos y la colección
db = cliente.chatbot
conversaciones = db.historial

# Función para guardar una interacción en la base de datos
def guardar_interaccion(texto: str, respuesta: str, emocion: str):
    """
    Guarda en la base de datos el mensaje del usuario, la respuesta del sistema y la emoción detectada.
    El mensaje se guarda de forma anonimizada para proteger la privacidad.
    """
    doc = {
        # Guardamos un hash del mensaje original
        "mensaje_hash": anonimizar_texto(texto),
        "respuesta_sistema": respuesta,
        "emocion": emocion,
        "timestamp": datetime.utcnow()  # Guardamos la fecha y hora en formato UTC
    }
    conversaciones.insert_one(doc)  # Insertamos el documento en la colección
