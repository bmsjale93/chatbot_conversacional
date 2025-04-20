from fastapi import APIRouter
from app.models.message import Message
from app.services.nlp_service import analizar_mensaje

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(mensaje: Message):
    respuesta = await analizar_mensaje(mensaje)

    # Si contiene error, construimos una respuesta válida para el frontend
    if "error" in respuesta:
        return {
            "mensaje": f"❌ Error interno: {respuesta['error']}",
            "estado": "fin",
            "sugerencias": []
        }

    # Si la respuesta ya es válida y tiene la estructura esperada
    return {
        "mensaje": respuesta.get("mensaje", "Respuesta no disponible."),
        "estado": respuesta.get("estado", "fin"),
        "sugerencias": respuesta.get("sugerencias", [])
    }
