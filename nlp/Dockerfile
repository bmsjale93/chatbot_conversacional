# Etapa 1: Construcción con dependencias pesadas y modelos
FROM nlp-base:latest as builder

WORKDIR /app

# Instalación de dependencias
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY . .

# Etapa 2: Imagen final ligera para producción
FROM python:3.9-slim

WORKDIR /app

# Configuración de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalación de dependencias mínimas del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev libssl-dev curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiamos dependencias de Python y binarios desde la etapa de construcción
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos la caché de modelos y el código fuente
COPY --from=builder /root/.cache /root/.cache
COPY . .

# Exponemos el puerto de la API
EXPOSE 8001

# Comando para iniciar el servicio NLP
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]
