import httpx
from app.models.message import Message

NLP_GESTIONAR_URL = "http://nlp:8001/gestionar"

async def analizar_mensaje(mensaje: Message):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            payload = {
                "session_id": mensaje.session_id,
                "mensaje_usuario": mensaje.mensaje_usuario
            }
            response = await client.post(NLP_GESTIONAR_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {
                "mensaje": f"❌ Error de conexión con el NLP: {str(e)}",
                "estado": "fin",
                "sugerencias": []
            }
        except httpx.HTTPStatusError as e:
            return {
                "mensaje": f"❌ Error HTTP desde NLP: {str(e)}",
                "estado": "fin",
                "sugerencias": []
            }
        except Exception as e:
            return {
                "mensaje": f"❌ Error inesperado procesando respuesta: {str(e)}",
                "estado": "fin",
                "sugerencias": []
            }
