from fastapi import APIRouter
from app.models.message import Message
from app.services.nlp_service import analizar_mensaje

# Creamos un router para agrupar las rutas relacionadas con el chatbot
router = APIRouter()

# Definimos un endpoint POST en la ruta "/chat"
@router.post("/chat")
async def chat_endpoint(mensaje: Message):
    # Llamamos de forma asíncrona al servicio de análisis de mensajes
    respuesta = await analizar_mensaje(mensaje)
    # Devolvemos la respuesta obtenida
    return respuesta
