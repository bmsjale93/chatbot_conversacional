import gradio as gr
import requests
import uuid
import os

# ------------------- Configuración -------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/chat")
HISTORIAL_URL = os.getenv("HISTORIAL_URL", "http://backend:8000/api/chat/historial")
conversacion_activa = True

# ------------------- Bienvenida -------------------
def crear_mensaje_bienvenida():
    return {
        "role": "assistant",
        "content": (
            "¡Bienvenido/a a tu espacio de escucha emocional!\n\n"
            "Este es un lugar seguro, confidencial y libre de juicios, donde podrás explorar cómo te sientes.\n\n"
            "Para comenzar, escribe simplemente 'Hola' o el mensaje que desees. Estoy aquí para ti."
        )
    }

# ------------------- Enviar mensaje -------------------
def enviar_mensaje(mensaje_usuario, historial, session_id):
    global conversacion_activa

    mensaje_usuario = mensaje_usuario.strip() if mensaje_usuario else ""
    mensaje_mostrado = mensaje_usuario if mensaje_usuario else "(entrada vacía)"

    if not conversacion_activa:
        historial.append({"role": "system", "content": "La conversación ha finalizado. Reinicia para comenzar de nuevo."})
        return historial, session_id, gr.update(visible=True), gr.update(visible=False)

    try:
        response = requests.post(
            BACKEND_URL,
            json={"session_id": session_id, "mensaje_usuario": mensaje_usuario},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        print("[DEBUG] Respuesta del backend:", data)

        mensaje_asistente = data.get("mensaje", "Respuesta no disponible en este momento.")
        estado = data.get("estado", "")
        sugerencias = data.get("sugerencias", [])
        modo_entrada = data.get("modo_entrada", "texto_libre")

        # Registrar siempre la entrada del usuario (aunque esté vacía)
        historial.append({"role": "user", "content": mensaje_mostrado})
        historial.append({"role": "assistant", "content": mensaje_asistente})

        if estado == "fin":
            conversacion_activa = False

        mostrar_texto = modo_entrada in ["texto_libre", "mixto"]
        mostrar_dropdown = modo_entrada in ["mixto", "sugerencias"] and bool(sugerencias)

        print("[DEBUG] modo_entrada:", modo_entrada)
        print("[DEBUG] sugerencias:", sugerencias)
        print("[DEBUG] mostrar_dropdown:", mostrar_dropdown)

        return (
            historial,
            session_id,
            gr.update(visible=mostrar_texto, value="", interactive=mostrar_texto),
            gr.update(
                visible=mostrar_dropdown,
                choices=sugerencias if mostrar_dropdown else [],
                value=None,
                interactive=mostrar_dropdown
            )
        )

    except requests.exceptions.RequestException as e:
        historial.append({"role": "system", "content": f"No se pudo contactar con el servidor: {e}"})
        return historial, session_id, gr.update(visible=True), gr.update(visible=False)

    except Exception as e:
        historial.append({"role": "system", "content": f"Ocurrió un error inesperado: {e}"})
        return historial, session_id, gr.update(visible=True), gr.update(visible=False)


# ------------------- Cargar historial -------------------
def cargar_historial(session_id):
    if not session_id or session_id == "null":
        session_id = str(uuid.uuid4())

    try:
        response = requests.get(f"{HISTORIAL_URL}?session_id={session_id}", timeout=5)
        response.raise_for_status()
        historial_guardado = response.json().get("historial", [])

        if not historial_guardado:
            return [crear_mensaje_bienvenida()], session_id, gr.update(visible=True), gr.update(visible=False)

        return historial_guardado, session_id, gr.update(visible=True), gr.update(visible=False)

    except Exception as e:
        print(f"[⚠️ ERROR AL CARGAR HISTORIAL] {e}")
        return [crear_mensaje_bienvenida()], session_id, gr.update(visible=True), gr.update(visible=False)

# ------------------- Reiniciar conversación -------------------
def reiniciar_conversacion():
    global conversacion_activa
    conversacion_activa = True
    nuevo_id = str(uuid.uuid4())

    return [crear_mensaje_bienvenida()], nuevo_id, gr.update(visible=True), gr.update(visible=False)

# ------------------- Interfaz Gradio -------------------
with gr.Blocks(theme=gr.themes.Soft()) as interfaz:
    session_state = gr.State()

    gr.Markdown("""
    # Asistente Virtual de Evaluación Emocional
    ---
    Este asistente conversacional está diseñado para ayudarte a reflexionar sobre tu estado emocional.  
    Puedes detener la conversación en cualquier momento.
    """)

    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            chat = gr.Chatbot(label="Historial de Conversación", height=600, type="messages")

        with gr.Column(scale=2):
            mensaje_input = gr.Textbox(
                placeholder="Escribe tu mensaje aquí...",
                label="Tu mensaje",
                lines=4,
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

    # ------------------- Eventos -------------------
    mensaje_input.submit(
        enviar_mensaje,
        inputs=[mensaje_input, chat, session_state],
        outputs=[chat, session_state, mensaje_input, sugerencias_dropdown]
    )

    boton_enviar.click(
        enviar_mensaje,
        inputs=[mensaje_input, chat, session_state],
        outputs=[chat, session_state, mensaje_input, sugerencias_dropdown]
    )

    sugerencias_dropdown.change(
        lambda sugerencia, historial, session_id:
            enviar_mensaje(sugerencia, historial, session_id) if sugerencia else
            (historial, session_id, gr.update(), gr.update()),
        inputs=[sugerencias_dropdown, chat, session_state],
        outputs=[chat, session_state, mensaje_input, sugerencias_dropdown]
    )

    boton_reiniciar.click(
        reiniciar_conversacion,
        outputs=[chat, session_state, mensaje_input, sugerencias_dropdown],
        js="""
        () => {
            localStorage.removeItem("session_id");
            return [[], null, "", []];
        }
        """
    )

    interfaz.load(
        fn=lambda session_id: cargar_historial(session_id),
        inputs=[session_state],
        outputs=[chat, session_state, mensaje_input, sugerencias_dropdown],
        js="""
            () => {
                let id = localStorage.getItem("session_id");
                if (!id) {
                    id = crypto.randomUUID();
                    localStorage.setItem("session_id", id);
                }
                return id;
            }
        """
    )

# ------------------- Lanzar -------------------
if __name__ == "__main__":
    interfaz.launch(server_name="0.0.0.0", server_port=7860, share=False)
