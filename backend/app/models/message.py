# Definir modelos de datos
from pydantic import BaseModel

# Definimos el modelo Message que representa el mensaje enviado por el usuario
class Message(BaseModel):
    # Campo que contiene el texto del mensaje del usuario
    mensaje_usuario: str
