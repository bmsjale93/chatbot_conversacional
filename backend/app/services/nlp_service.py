# Peticiones HTTP de forma asíncrona
import httpx
from app.models.message import Message

# Nueva URL del microservicio NLP para flujo completo
NLP_GESTIONAR_URL = "http://nlp:8001/gestionar"

# Función asíncrona que envía el mensaje al microservicio NLP y obtiene una respuesta completa
async def analizar_mensaje(mensaje: Message):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(NLP_GESTIONAR_URL, json=mensaje.model_dump())
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
