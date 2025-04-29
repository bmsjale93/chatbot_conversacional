import gradio as gr
import requests
import uuid
import os

# ------------------- Configuración -------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/chat")
session_id = str(uuid.uuid4())
conversacion_activa = True

# ------------------- Función principal -------------------
def enviar_mensaje(mensaje_usuario: str, historial: list) -> tuple:
    global conversacion_activa

    if not conversacion_activa:
        historial.append(
            ("Sistema", "La conversación ha finalizado. Reinicia para comenzar de nuevo."))
        return historial, "", gr.update(visible=False, choices=[])

    mensaje_usuario = mensaje_usuario.strip()
    if not mensaje_usuario:
        historial.append(
            ("Sistema", "Por favor, escribe un mensaje para continuar."))
        return historial, "", gr.update(visible=False, choices=[])

    try:
        response = requests.post(
            BACKEND_URL,
            json={"session_id": session_id, "mensaje_usuario": mensaje_usuario},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        mensaje_asistente = data.get(
            "mensaje", "Respuesta no disponible en este momento.")
        estado = data.get("estado", "")
        sugerencias = data.get("sugerencias", [])

        historial.append(("Usuario", mensaje_usuario))
        historial.append(("Asistente", mensaje_asistente))

        if estado == "fin":
            conversacion_activa = False

        return historial, "", gr.update(visible=bool(sugerencias), choices=sugerencias)

    except requests.exceptions.RequestException as e:
        historial.append(
            ("Error", f"No se pudo contactar con el servidor: {e}"))
        return historial, "", gr.update(visible=False, choices=[])

    except Exception as e:
        historial.append(("Error", f"Ocurrió un error inesperado: {e}"))
        return historial, "", gr.update(visible=False, choices=[])

# ------------------- Reinicio de Conversación -------------------


def reiniciar_conversacion() -> tuple:
    global session_id, conversacion_activa
    session_id = str(uuid.uuid4())
    conversacion_activa = True
    return [], "", gr.update(visible=False, choices=[])


# ------------------- Interfaz Gradio -------------------
with gr.Blocks(theme=gr.themes.Soft()) as interfaz:
    gr.Markdown(
        """
        # Asistente Virtual de Evaluación Emocional
        ---
        Este asistente conversacional está diseñado para ayudarte a reflexionar sobre tu estado emocional.  
        Puedes detener la conversación en cualquier momento.
        """,
        elem_id="titulo"
    )

    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            chat = gr.Chatbot(label="Historial de Conversación", height=600)

        with gr.Column(scale=2):
            mensaje_input = gr.Textbox(
                placeholder="Escribe tu mensaje aquí...",
                label="Tu mensaje",
                lines=4,
                autofocus=True
            )

            sugerencias = gr.Dropdown(
                choices=[],
                visible=False,
                label="Sugerencias disponibles"
            )

            boton_enviar = gr.Button("Enviar mensaje", variant="primary")
            boton_reiniciar = gr.Button(
                "Reiniciar conversación", variant="secondary")

            gr.Markdown(
                """
                **Instrucciones rápidas:**
                - Puedes escribir con libertad.
                - Usa las sugerencias si no sabes qué responder.
                - El botón de reinicio te permite empezar de nuevo.
                """,
                elem_id="instrucciones"
            )

    # Eventos
    mensaje_input.submit(enviar_mensaje, [mensaje_input, chat], [
                         chat, mensaje_input, sugerencias])
    boton_enviar.click(enviar_mensaje, [mensaje_input, chat], [
                       chat, mensaje_input, sugerencias])
    boton_reiniciar.click(reiniciar_conversacion, outputs=[
                          chat, mensaje_input, sugerencias])
    sugerencias.change(enviar_mensaje, [sugerencias, chat], [
                       chat, mensaje_input, sugerencias])


# ------------------- Lanzar Interfaz -------------------
if __name__ == "__main__":
    interfaz.launch(server_name="0.0.0.0", server_port=7860, share=False)
