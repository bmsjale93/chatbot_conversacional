from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.message import Message
from app.services.nlp_service import analizar_mensaje

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(mensaje: Message):
    """
    Endpoint principal para recibir mensajes del usuario y obtener una respuesta emocional.
    """
    respuesta = await analizar_mensaje(mensaje)

    if "error" in respuesta:
        return JSONResponse(
            status_code=500,
            content={
                "mensaje": f"❌ Error interno: {respuesta['error']}",
                "estado": "fin",
                "sugerencias": []
            }
        )

    return {
        "mensaje": respuesta.get("mensaje", "Respuesta no disponible."),
        "estado": respuesta.get("estado", "fin"),
        "sugerencias": respuesta.get("sugerencias", [])
    }
