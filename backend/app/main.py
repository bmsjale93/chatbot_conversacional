# Importamos FastAPI para crear la aplicación web
from fastapi import FastAPI
from app.routes import chatbot

# Creamos una instancia de la aplicación FastAPI
app = FastAPI()

# Incluimos las rutas definidas en el archivo chatbot.py
app.include_router(chatbot.router)

# Definimos un endpoint GET en la raíz ("/") para comprobar que la API está activa
@app.get("/")
async def home():
    return {"message": "API funcionando correctamente"}
