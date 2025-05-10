from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.message import Message
from app.services.nlp_service import analizar_mensaje
from app.services.historial_service import recuperar_historial
import traceback

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(mensaje: Message):
    """
    Procesa el mensaje del usuario y devuelve una respuesta emocional.
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
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "mensaje": f"❌ Error inesperado en backend: {str(e)}",
                "estado": "fin",
                "sugerencias": []
            }
        )

@router.get("/chat/historial")
async def obtener_historial(session_id: str):
    """
    Recupera el historial completo de una sesión.
    """
    try:
        historial = recuperar_historial(session_id)
        return {"historial": historial}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"mensaje": f"❌ Error al recuperar historial: {str(e)}"}
        )
