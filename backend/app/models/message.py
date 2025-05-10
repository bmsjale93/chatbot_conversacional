from pydantic import BaseModel, Field

class Message(BaseModel):
    session_id: str = Field(..., min_length=1, description="Identificador único de la sesión.")
    mensaje_usuario: str = Field(..., description="Mensaje enviado por el usuario.")
