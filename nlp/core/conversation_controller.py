from core.conversation_state import obtener_estado_usuario, guardar_estado_usuario, borrar_estado_usuario
from core.conversation_flow import procesar_mensaje


def gestionar_mensaje(session_id: str, texto_usuario: str) -> dict:
    """
    Controlador maestro de la conversación:
    - Recupera el estado actual del usuario desde Redis.
    - Procesa el mensaje recibido según el estado.
    - Actualiza o elimina el estado tras procesar.
    - Devuelve el próximo mensaje que el asistente debe mostrar.
    """

    # 1. Recuperar el estado actual de la conversación desde Redis
    estado_usuario = obtener_estado_usuario(session_id)

    if not estado_usuario:
        # Primera interacción: crear estado inicial
        estado_usuario = {
            "estado_actual": "presentacion",
            "datos_guardados": {}
        }
        guardar_estado_usuario(session_id, estado_usuario)

    estado_actual = estado_usuario.get("estado_actual", "presentacion")
    datos_guardados = estado_usuario.get("datos_guardados", {})

    # 2. Procesar el nuevo mensaje recibido
    respuesta, datos_guardados_actualizados = procesar_mensaje(
        session_id, texto_usuario, estado_actual, datos_guardados
    )

    # 3. Comprobar cuál es el nuevo estado después de procesar
    nuevo_estado = respuesta.get("estado")

    if nuevo_estado and nuevo_estado != "fin":
        # Si la conversación continúa, actualizamos el estado y los datos guardados
        guardar_estado_usuario(session_id, {
            "estado_actual": nuevo_estado,
            "datos_guardados": datos_guardados_actualizados
        })
    else:
        # Si finaliza, eliminamos el estado para liberar memoria
        borrar_estado_usuario(session_id)

    # 4. Devolver la respuesta que el asistente debe enviar al usuario
    return respuesta
