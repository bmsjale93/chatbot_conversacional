from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import chatbot
import os

# ---------------------- Creación de la Aplicación ----------------------
app = FastAPI(
    title="Asistente Virtual API",
    description="API de backend para gestión de mensajes de evaluación emocional.",
    version="1.0.0"
)

# ---------------------- Configuración de CORS ----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- Servir archivos estáticos (PDFs) ----------------------
# Verifica que la carpeta exista para evitar errores al montar
os.makedirs("static/informes", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------- Inclusión de Rutas ----------------------
app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])

# ---------------------- Endpoints del Sistema ----------------------
@app.get("/", tags=["Sistema"])
async def home():
    return {
        "message": "✅ API funcionando correctamente. Usa /api/chat para interactuar.",
        "descarga_informes": "/static/informes/{nombre_archivo}.pdf"
    }
