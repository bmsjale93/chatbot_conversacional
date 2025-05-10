# Imagen base ligera con Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para Gradio (audio, video, red)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configuración del entorno Python para evitar archivos pyc y mostrar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copia el archivo de requerimientos y los instala sin usar caché
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al contenedor
COPY . .

# Comando de arranque: lanza la aplicación Gradio
CMD ["python", "app_gradio.py"]
