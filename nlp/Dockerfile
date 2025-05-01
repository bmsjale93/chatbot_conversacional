### ETAPA 1: Construcción con dependencias pesadas y modelos ###
FROM nlp-base:latest as builder

WORKDIR /app

# Copiamos sólo lo necesario para aprovechar la cache
COPY requirements.txt .

# Instalamos dependencias Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código fuente para precompilar si es necesario
COPY . .

# Pre-descarga del modelo (precaución: se espera que esto ocurra en el base también)
# Esto asegura que Hugging Face cache esté poblado antes del paso final

### ETAPA 2: Imagen final ligera para producción ###
FROM python:3.9-slim

WORKDIR /app

# Variables para evitar pyc y mantener logs visibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Dependencias mínimas necesarias en entorno ligero
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev libssl-dev curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiamos librerías de Python desde la fase anterior
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos caché de modelos descargados previamente
COPY --from=builder /root/.cache /root/.cache

# Copiamos el código fuente de la app
COPY . .

# Puerto para la API NLP
EXPOSE 8001

# Comando para iniciar la API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]