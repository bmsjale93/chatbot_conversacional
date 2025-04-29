from typing import Dict

from core.conversation_state import (
    obtener_estado_usuario,
    guardar_estado_usuario,
    borrar_estado_usuario
)
from core.conversation_flow import procesar_mensaje

# Constantes para estados especiales
ESTADO_INICIAL = "presentacion"
ESTADO_FINAL = "fin"


def gestionar_mensaje(session_id: str, texto_usuario: str) -> Dict:
    """
    Controlador maestro de la conversación:
    1. Recupera el estado actual del usuario desde Redis (si existe).
    2. Procesa el mensaje recibido con base en el estado actual.
    3. Guarda o elimina el nuevo estado según si la conversación continúa o finaliza.
    4. Devuelve la respuesta que debe mostrar el asistente.

    Args:
        session_id (str): ID de sesión único del usuario.
        texto_usuario (str): Mensaje de entrada enviado por el usuario.

    Returns:
        dict: Estructura con el nuevo estado, mensaje de respuesta y sugerencias.
    """
    if not session_id or not texto_usuario:
        return {
            "estado": ESTADO_FINAL,
            "mensaje": "❌ Sesión inválida o mensaje vacío.",
            "sugerencias": []
        }

    # Paso 1: Recuperar o inicializar el estado del usuario
    estado_usuario = obtener_estado_usuario(session_id)

    if not estado_usuario:
        estado_usuario = {
            "estado_actual": ESTADO_INICIAL,
            "datos_guardados": {}
        }
        guardar_estado_usuario(session_id, estado_usuario)

    estado_actual = estado_usuario.get("estado_actual", ESTADO_INICIAL)
    datos_guardados = estado_usuario.get("datos_guardados", {})

    # Paso 2: Procesar el mensaje según el estado actual
    respuesta, datos_guardados_actualizados = procesar_mensaje(
        session_id, texto_usuario, estado_actual, datos_guardados
    )

    # Paso 3: Actualizar o eliminar el estado según el flujo
    nuevo_estado = respuesta.get("estado")

    if nuevo_estado and nuevo_estado != ESTADO_FINAL:
        guardar_estado_usuario(session_id, {
            "estado_actual": nuevo_estado,
            "datos_guardados": datos_guardados_actualizados
        })
    else:
        borrar_estado_usuario(session_id)

    # Paso 4: Devolver respuesta del asistente
    return respuesta
