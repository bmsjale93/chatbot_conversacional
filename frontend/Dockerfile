# Imagen ligera con Python 3.10
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (si Gradio usa audio o vídeo puede requerir ffmpeg y curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Evitar archivos pyc y mantener logs visibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copiamos el archivo de dependencias
COPY requirements.txt .

# Instalamos dependencias Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código fuente
COPY . .

# Comando para lanzar la aplicación Gradio
CMD ["python", "app_gradio.py"]
