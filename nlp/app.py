# Importamos FastAPI para crear la API
from fastapi import FastAPI
# Importamos BaseModel para definir modelos de datos
from pydantic import BaseModel
from core.response_generator import generar_respuesta

# Creamos una instancia de la aplicación FastAPI
app = FastAPI()

# Definimos el modelo de entrada del usuario
class MensajeEntrada(BaseModel):
    mensaje_usuario: str

# Definimos el modelo de salida de la respuesta
class RespuestaSalida(BaseModel):
    estado_emocional: str
    respuesta: str

# Definimos un endpoint POST en "/analyze" que analiza el mensaje del usuario
@app.post("/analyze", response_model=RespuestaSalida)
async def analizar(mensaje: MensajeEntrada):
    # Generamos la respuesta usando el texto recibido
    resultado = generar_respuesta(mensaje.mensaje_usuario)
    # Devolvemos la respuesta adaptada al modelo de salida
    return RespuestaSalida(**resultado)
