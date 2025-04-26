# Importamos FastAPI para crear la aplicación web
from fastapi import FastAPI
from app.routes import chatbot

# Creamos una instancia de la aplicación FastAPI
app = FastAPI(
    title="Asistente Virtual API",
    description="API de backend para gestión de mensajes de evaluación emocional.",
    version="1.0.0"
)

# Incluimos las rutas definidas, bajo un prefijo /api
app.include_router(chatbot.router, prefix="/api")

# Endpoint para comprobar que la API está funcionando
@app.get("/", tags=["Sistema"])
async def home():
    return {"message": "✅ API funcionando correctamente. Usa /api/chat para interactuar."}
