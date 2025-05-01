# Imagen base ligera con Python 3.9
FROM python:3.9-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias para algunas librerías (opcional si lo necesitas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev libssl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiamos primero el archivo de dependencias (para usar la cache)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la aplicación
COPY . .

# Puerto expuesto (FastAPI por defecto)
EXPOSE 8000

# Variable de entorno para prevenir que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Comando para lanzar la app en producción
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
