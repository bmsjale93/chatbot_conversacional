from pydantic import BaseModel, Field


class Message(BaseModel):
    session_id: str = Field(..., min_length=1,
                            description="ID único de la sesión del usuario.")
    mensaje_usuario: str = Field(..., min_length=1,
                                 description="Mensaje enviado por el usuario.")
