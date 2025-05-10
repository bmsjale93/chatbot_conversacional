import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Base de datos
DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017/chatbot")

# Clave secreta
SECRET_KEY: str = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("⚠️ Advertencia: SECRET_KEY no está definida. Algunas funcionalidades podrían fallar.")

# URL del servicio NLP
NLP_GESTIONAR_URL: str = os.getenv("NLP_GESTIONAR_URL", "http://nlp:8001/gestionar")
