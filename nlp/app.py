from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from core.response_generator import generar_respuesta
from core.conversation_controller import gestionar_mensaje

app = FastAPI(
    title="Servicio NLP Asistente Virtual",
    description="Servicio NLP que analiza emociones y gestiona el flujo de conversación emocional.",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montaje de carpeta estática para archivos PDF
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelos de entrada/salida
class MensajeEntrada(BaseModel):
    mensaje_usuario: str

class PayloadGestionar(BaseModel):
    session_id: str
    mensaje_usuario: str

class RespuestaSalida(BaseModel):
    mensaje: str
    estado: str
    sugerencias: list[str] = []

# Endpoints principales
@app.get("/", tags=["Sistema"])
async def home():
    return {
        "mensaje": "Servicio NLP activo. Usa /gestionar para conversación completa o /analyze para respuesta directa."
    }

@app.post("/analyze", response_model=RespuestaSalida, tags=["Análisis emocional"])
async def analizar(mensaje: MensajeEntrada):
    resultado = generar_respuesta(mensaje.mensaje_usuario)
    return RespuestaSalida(
        mensaje=resultado["respuesta"],
        estado=resultado.get("estado", "fin"),
        sugerencias=resultado.get("sugerencias", [])
    )

@app.post("/gestionar", tags=["Conversación emocional"])
async def gestionar(payload: PayloadGestionar):
    try:
        return gestionar_mensaje(payload.session_id, payload.mensaje_usuario)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el mensaje: {str(e)}"
        )
