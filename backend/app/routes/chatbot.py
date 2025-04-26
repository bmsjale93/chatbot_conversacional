from fastapi import APIRouter
from app.models.message import Message
from app.services.nlp_service import analizar_mensaje

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(mensaje: Message):
    # Validación básica extra (aunque FastAPI ya valida estructura con Pydantic)
    if not mensaje.session_id or not mensaje.mensaje_usuario:
        return {
            "mensaje": "❌ Error: falta session_id o mensaje_usuario.",
            "estado": "fin",
            "sugerencias": []
        }

    respuesta = await analizar_mensaje(mensaje)

    if "error" in respuesta:
        return {
            "mensaje": f"❌ Error interno: {respuesta['error']}",
            "estado": "fin",
            "sugerencias": []
        }

    return {
        "mensaje": respuesta.get("mensaje", "Respuesta no disponible."),
        "estado": respuesta.get("estado", "fin"),
        "sugerencias": respuesta.get("sugerencias", [])
    }
