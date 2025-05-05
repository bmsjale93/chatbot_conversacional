import gradio as gr
import requests
import uuid
import os

# ------------------- Configuración -------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/chat")
session_id = str(uuid.uuid4())
conversacion_activa = True

# ------------------- Función principal -------------------
def enviar_mensaje(mensaje_usuario, historial):
    global conversacion_activa

    mensaje_usuario = mensaje_usuario.strip() if mensaje_usuario else ""

    if not conversacion_activa:
        historial.append({"role": "system", "content": "La conversación ha finalizado. Reinicia para comenzar de nuevo."})
        return historial, gr.update(visible=True, value="", interactive=True), gr.update(visible=False, interactive=False, choices=[])

    if not mensaje_usuario:
        return historial, gr.update(value="", interactive=True), gr.update(interactive=False)

    try:
        response = requests.post(
            BACKEND_URL,
            json={"session_id": session_id, "mensaje_usuario": mensaje_usuario},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        print("⚙️ RESPUESTA DEL BACKEND:", data)

        mensaje_asistente = data.get("mensaje", "Respuesta no disponible en este momento.")
        estado = data.get("estado", "")
        sugerencias = data.get("sugerencias", [])
        modo_entrada = data.get("modo_entrada", "texto_libre")

        historial.append({"role": "user", "content": mensaje_usuario})
        historial.append({"role": "assistant", "content": mensaje_asistente})

        if estado == "fin":
            conversacion_activa = False

        # Mostrar el campo de texto si el modo lo permite (texto libre o mixto)
        mostrar_texto = modo_entrada in ["texto_libre", "mixto"]

        # Mostrar sugerencias si hay alguna, sin importar el modo
        mostrar_dropdown = bool(sugerencias)

        return (
            historial,
            gr.update(visible=mostrar_texto, value="", interactive=mostrar_texto),
            gr.update(visible=mostrar_dropdown, choices=sugerencias, value=None, interactive=mostrar_dropdown)
        )

    except requests.exceptions.RequestException as e:
        historial.append({"role": "system", "content": f"No se pudo contactar con el servidor: {e}"})
        return historial, gr.update(visible=True, value="", interactive=True), gr.update(visible=False, interactive=False, choices=[])

    except Exception as e:
        historial.append({"role": "system", "content": f"Ocurrió un error inesperado: {e}"})
        return historial, gr.update(visible=True, value="", interactive=True), gr.update(visible=False, interactive=False, choices=[])

# ------------------- Reinicio de Conversación -------------------
def reiniciar_conversacion():
    global session_id, conversacion_activa
    session_id = str(uuid.uuid4())
    conversacion_activa = True
    return [], gr.update(visible=True, value="", interactive=True), gr.update(visible=False, interactive=False, choices=[])

# ------------------- Interfaz Gradio -------------------
with gr.Blocks(theme=gr.themes.Soft()) as interfaz:
    gr.Markdown(
        """
        # Asistente Virtual de Evaluación Emocional
        ---
        Este asistente conversacional está diseñado para ayudarte a reflexionar sobre tu estado emocional.  
        Puedes detener la conversación en cualquier momento.
        """
    )

    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            chat = gr.Chatbot(label="Historial de Conversación", height=600, type="messages")

        with gr.Column(scale=2):
            mensaje_input = gr.Textbox(
                placeholder="Escribe tu mensaje aquí...",
                label="Tu mensaje",
                lines=4,
                autofocus=True,
                visible=True,
                interactive=True
            )

            sugerencias_dropdown = gr.Dropdown(
                choices=[],
                visible=False,
                interactive=False,
                label="Sugerencias disponibles"
            )

            boton_enviar = gr.Button("Enviar mensaje", variant="primary")
            boton_reiniciar = gr.Button("Reiniciar conversación", variant="secondary")

            gr.Markdown(
                """
                **Instrucciones rápidas:**
                - Puedes escribir con libertad cuando el campo esté disponible.
                - Usa las sugerencias cuando se muestren.
                - El botón de reinicio te permite empezar de nuevo.
                """
            )

    # ------------------- Eventos -------------------
    def wrapper_enviar_mensaje(mensaje_usuario, historial):
        return enviar_mensaje(mensaje_usuario, historial)

    def wrapper_sugerencia_elegida(sugerencia, historial):
        if sugerencia:
            return enviar_mensaje(sugerencia, historial)
        return historial, gr.update(), gr.update()

    mensaje_input.submit(wrapper_enviar_mensaje, [mensaje_input, chat], [chat, mensaje_input, sugerencias_dropdown])
    boton_enviar.click(wrapper_enviar_mensaje, [mensaje_input, chat], [chat, mensaje_input, sugerencias_dropdown])
    sugerencias_dropdown.change(wrapper_sugerencia_elegida, [sugerencias_dropdown, chat], [chat, mensaje_input, sugerencias_dropdown])
    boton_reiniciar.click(reiniciar_conversacion, outputs=[chat, mensaje_input, sugerencias_dropdown])

# ------------------- Lanzar Interfaz -------------------
if __name__ == "__main__":
    interfaz.launch(server_name="0.0.0.0", server_port=7860, share=False)
