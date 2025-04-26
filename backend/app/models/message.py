from pydantic import BaseModel

class Message(BaseModel):
    # ID de sesión del usuario (para controlar la conversación)
    session_id: str
    
    # Texto del mensaje que envía el usuario
    mensaje_usuario: str
