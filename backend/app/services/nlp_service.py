import httpx
from app.models.message import Message
from app.config import NLP_GESTIONAR_URL  # Se mueve la URL a config


async def analizar_mensaje(mensaje: Message) -> dict:
    """
    Envía el mensaje al servicio NLP y devuelve la respuesta estructurada.
    """
    payload = {
        "session_id": mensaje.session_id,
        "mensaje_usuario": mensaje.mensaje_usuario
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(NLP_GESTIONAR_URL, json=payload)
            response.raise_for_status()
            return response.json()

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        error_msg = "Error de conexión con el NLP" if isinstance(
            e, httpx.RequestError) else "Error HTTP desde NLP"
        return _respuesta_error(f"{error_msg}: {str(e)}")

    except Exception as e:
        return _respuesta_error(f"Error inesperado procesando respuesta: {str(e)}")


def _respuesta_error(mensaje_error: str) -> dict:
    """
    Devuelve una estructura estándar de error para NLP.
    """
    return {
        "error": mensaje_error,
        "mensaje": f"❌ {mensaje_error}",
        "estado": "fin",
        "sugerencias": []
    }
