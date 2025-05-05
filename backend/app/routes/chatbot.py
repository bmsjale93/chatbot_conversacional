from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.message import Message
from app.services.nlp_service import analizar_mensaje
import traceback

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(mensaje: Message):
    """
    Endpoint principal para recibir mensajes del usuario y obtener una respuesta emocional.
    """
    try:
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
            "sugerencias": respuesta.get("sugerencias", []),
            "modo_entrada": respuesta.get("modo_entrada", "texto_libre")
        }

    except Exception as e:
        # Mostramos la traza exacta en los logs del backend
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "mensaje": f"❌ Error inesperado en backend: {str(e)}",
                "estado": "fin",
                "sugerencias": []
            }
        )
