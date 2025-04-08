# Cargar variables de entorno desde un archivo .env
from dotenv import load_dotenv
import os

# Cargamos las variables definidas en el archivo .env
load_dotenv()

# Obtenemos la URL de la base de datos, con un valor por defecto si no está definida
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/chatbot")

# Obtenemos la clave secreta usada para temas de seguridad (por ejemplo, autenticación)
SECRET_KEY = os.getenv("SECRET_KEY")