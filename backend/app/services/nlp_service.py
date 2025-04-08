# Peticiones HTTP de forma asíncrona
import httpx
from app.models.message import Message

# URL del microservicio NLP (usando el nombre del contenedor en la red de Docker)
NLP_URL = "http://nlp:8001/analyze"

# Función asíncrona que envía el mensaje al microservicio NLP y obtiene una respuesta
async def analizar_mensaje(mensaje: Message):
    # Creamos un cliente HTTP asíncrono con un timeout de 5 segundos
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # Enviamos el mensaje al microservicio en formato JSON
            # Usamos model_dump() para convertir el modelo Pydantic a diccionario
            response = await client.post(NLP_URL, json=mensaje.model_dump())
            # Lanza error si el estado HTTP no es 200 OK
            response.raise_for_status()
            # Devolvemos la respuesta del microservicio en formato JSON
            return response.json()
        except httpx.RequestError as e:
            # Error si no se pudo conectar al servicio NLP
            return {"error": f"No se pudo conectar al servicio NLP: {str(e)}"}
        except httpx.HTTPStatusError as e:
            # Error si el servicio NLP respondió con un código de error
            return {"error": f"Error en la respuesta del servicio NLP: {str(e)}"}
