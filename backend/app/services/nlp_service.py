import httpx
import traceback
from app.models.message import Message
from app.config import NLP_GESTIONAR_URL

async def analizar_mensaje(mensaje: Message) -> dict:
    """
    Envía el mensaje al servicio NLP y devuelve la respuesta estructurada.
    """
    payload = {
        "session_id": mensaje.session_id,
        "mensaje_usuario": mensaje.mensaje_usuario
    }

    try:
        print("[DEBUG] Enviando payload al NLP:", payload)

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(NLP_GESTIONAR_URL, json=payload)
            response.raise_for_status()
            json_data = response.json()

            print("[DEBUG] Respuesta recibida del NLP:", json_data)
            return json_data

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        error_msg = "Error de conexión con el NLP" if isinstance(
            e, httpx.RequestError) else "Error HTTP desde NLP"
        print(f"[ERROR NLP] {error_msg}: {str(e)}")
        return _respuesta_error(f"{error_msg}: {str(e)}")

    except Exception as e:
        print("[ERROR NLP] Excepción inesperada:")
        traceback.print_exc()
        return _respuesta_error(f"Error inesperado procesando respuesta: {str(e)}")

def _respuesta_error(mensaje_error: str) -> dict:
    """
    Estructura estándar de respuesta en caso de error al contactar con el servicio NLP.
    """
    return {
        "error": mensaje_error,
        "mensaje": f"❌ {mensaje_error}",
        "estado": "fin",
        "sugerencias": []
    }
