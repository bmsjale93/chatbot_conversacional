import os
from dotenv import load_dotenv

# Cargamos variables de entorno desde el archivo .env
load_dotenv()

# ---------------------- Configuración de la Base de Datos ----------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "mongodb://localhost:27017/chatbot")

# ---------------------- Seguridad ----------------------
SECRET_KEY: str = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("⚠️ Advertencia: SECRET_KEY no está definida. Algunas funcionalidades podrían fallar.")

# ---------------------- Servicios Externos ----------------------
NLP_GESTIONAR_URL: str = os.getenv(
    "NLP_GESTIONAR_URL", "http://nlp:8001/gestionar")
