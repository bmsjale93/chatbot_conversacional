from fastapi import FastAPI
from pydantic import BaseModel
from core.response_generator import generar_respuesta
from core.conversation_controller import gestionar_mensaje

app = FastAPI()

class MensajeEntrada(BaseModel):
    mensaje_usuario: str

class RespuestaSalida(BaseModel):
    mensaje: str
    estado: str
    sugerencias: list[str] = []

@app.post("/analyze", response_model=RespuestaSalida)
async def analizar(mensaje: MensajeEntrada):
    resultado = generar_respuesta(mensaje.mensaje_usuario)

    return RespuestaSalida(
        mensaje=resultado["respuesta"],
        estado=resultado.get("estado", "fin"),
        sugerencias=resultado.get("sugerencias", [])
    )

@app.post("/gestionar")
async def gestionar(payload: dict):
    session_id = payload.get("session_id")
    mensaje_usuario = payload.get("mensaje_usuario")

    if not session_id or not mensaje_usuario:
        return {"mensaje": "❌ Faltan datos: session_id o mensaje_usuario", "estado": "fin", "sugerencias": []}

    try:
        respuesta = gestionar_mensaje(session_id, mensaje_usuario)
        return respuesta
    except Exception as e:
        return {
            "mensaje": f"❌ Error al procesar el mensaje: {str(e)}",
            "estado": "fin",
            "sugerencias": []
        }
