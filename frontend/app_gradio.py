import gradio as gr
import requests
import uuid

# URL del backend FastAPI (ajusta si ejecutas en local fuera de Docker)
BACKEND_URL = "http://backend:8000/chat"

# Generamos un session_id único por sesión
session_id = str(uuid.uuid4())

# Estado global de conversación
conversacion_activa = True


def enviar_mensaje(mensaje_usuario, historial):
    global conversacion_activa

    if not conversacion_activa:
        return historial + [("", "⚠️ La conversación ha finalizado.")], "", gr.update(visible=False, choices=[])

    if not mensaje_usuario.strip():
        return historial + [("", "⚠️ Por favor, escribe algo para continuar.")], "", gr.update(visible=False, choices=[])

    try:
        respuesta = requests.post(
            BACKEND_URL,
            json={
                "session_id": session_id,
                "mensaje_usuario": mensaje_usuario
            },
            timeout=10
        )
        respuesta.raise_for_status()
        data = respuesta.json()
        mensaje_asistente = data.get(
            "mensaje", "No se recibió una respuesta válida.")
        estado = data.get("estado", "")
        sugerencias = data.get("sugerencias", [])

        historial = historial + [(mensaje_usuario, mensaje_asistente)]

        if estado == "fin":
            conversacion_activa = False

        return historial, "", gr.update(visible=bool(sugerencias), choices=sugerencias)

    except requests.exceptions.RequestException as e:
        historial.append(
            (mensaje_usuario, f"❌ Error al contactar con el backend: {e}"))
        return historial, "", gr.update(visible=False, choices=[])

    except Exception as e:
        historial.append((mensaje_usuario, f"❌ Error interno inesperado: {e}"))
        return historial, "", gr.update(visible=False, choices=[])


def reiniciar_conversacion():
    global session_id, conversacion_activa
    session_id = str(uuid.uuid4())
    conversacion_activa = True
    return [], "", gr.update(visible=False, choices=[])


# Interfaz visual con Gradio
with gr.Blocks() as interfaz:
    gr.Markdown("## 🤖 Asistente Virtual de Evaluación Emocional")
    gr.Markdown("Habla conmigo para explorar cómo te has sentido últimamente.")

    chat = gr.Chatbot(label="Conversación")
    mensaje_input = gr.Textbox(
        placeholder="Escribe tu mensaje aquí...", label="Tu mensaje", lines=2)
    sugerencias = gr.Dropdown(
        choices=[], visible=False, label="¿Quieres usar una sugerencia rápida?")
    boton_enviar = gr.Button("Enviar")
    boton_reiniciar = gr.Button("🔄 Reiniciar Conversación")

    # Acciones
    mensaje_input.submit(fn=enviar_mensaje, inputs=[mensaje_input, chat], outputs=[
                         chat, mensaje_input, sugerencias])
    boton_enviar.click(fn=enviar_mensaje, inputs=[mensaje_input, chat], outputs=[
                       chat, mensaje_input, sugerencias])
    boton_reiniciar.click(fn=reiniciar_conversacion, outputs=[
                          chat, mensaje_input, sugerencias])
    sugerencias.change(fn=enviar_mensaje, inputs=[sugerencias, chat], outputs=[
                       chat, mensaje_input, sugerencias])

# Lanzar servidor Gradio
if __name__ == "__main__":
    interfaz.launch(server_name="0.0.0.0", server_port=7860, share=False)
