# Fase de construcción: imagen base personalizada con dependencias pesadas
FROM nlp-base:latest as builder

# Establecemos el directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos sólo el archivo de requerimientos para aprovechar la cache
COPY requirements.txt .

# Instalamos las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Fase final: imagen ligera para producción
FROM python:3.9-slim

# Establecemos nuevamente el directorio de trabajo
WORKDIR /app

# Copiamos las librerías instaladas desde el contenedor de construcción
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos los modelos descargados en la caché
COPY --from=builder /root/.cache /root/.cache

# Copiamos el código fuente de la aplicación
COPY . .

# Exponemos el puerto 8001 para que FastAPI escuche
EXPOSE 8001

# Comando para ejecutar el servidor Uvicorn al iniciar el contenedor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
