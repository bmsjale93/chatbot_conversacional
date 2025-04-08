# Usamos una imagen ligera de Python 3.9
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el archivo de dependencias para aprovechar la cache de Docker
COPY requirements.txt .

# Instalamos las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de los archivos del proyecto
COPY . .

# Exponemos el puerto 8000 para acceder a la aplicación
EXPOSE 8000

# Comando para arrancar la aplicación usando Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
