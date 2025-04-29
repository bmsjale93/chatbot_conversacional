from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chatbot

# ---------------------- Creación de la Aplicación ----------------------
app = FastAPI(
    title="Asistente Virtual API",
    description="API de backend para gestión de mensajes de evaluación emocional.",
    version="1.0.0"
)

# ---------------------- Configuración de CORS ----------------------
app.add_middleware(
    CORSMiddleware,
    # Permitir todos los orígenes (ajustable en producción)
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- Inclusión de Rutas ----------------------
app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])

# ---------------------- Endpoints del Sistema ----------------------


@app.get("/", tags=["Sistema"])
async def home():
    return {"message": "✅ API funcionando correctamente. Usa /api/chat para interactuar."}
