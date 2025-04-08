# Sistema de Análisis Emocional y Moderación de Chat

## Introducción

Este proyecto desarrolla un **backend modularizado** que permite analizar mensajes de texto enviados por los usuarios, detectar su **estado emocional** y moderar el contenido de forma segura antes de responder.  
Todo el sistema se encuentra **contenedorizado con Docker** para facilitar su despliegue, escalabilidad y mantenimiento.

### Objetivos principales:

- **Análisis emocional automático:** utilizando modelos de procesamiento de lenguaje natural (NLP) basados en BERT entrenado en español.
- **Moderación de contenido:** detectando lenguaje ofensivo, palabras prohibidas o riesgos potenciales.
- **Generación de respuestas empáticas:** adaptadas al estado emocional detectado.
- **Anonimización y almacenamiento seguro:** para cumplir con buenas prácticas de privacidad y seguridad de datos.
- **Arquitectura de microservicios:** backend y NLP funcionando de forma independiente pero conectados.

## Tecnologías y herramientas utilizadas:

| Tecnología         | Propósito                                           |
|:-------------------|:-----------------------------------------------------|
| **FastAPI**         | API REST backend, rápida y moderna                   |
| **Docker & Docker Compose** | Contenerización y orquestación de servicios |
| **MongoDB**         | Base de datos NoSQL para almacenar interacciones     |
| **Redis**           | Cache de respuestas para optimizar latencia          |
| **Transformers (Hugging Face)** | Modelos NLP para análisis de sentimientos |
| **PyMongo**         | Conexión eficiente con MongoDB desde Python          |
| **pytest / scripts de test** | Pruebas unitarias para garantizar calidad    |


## ¿Qué incluye este proyecto?

- **Microservicio NLP**: procesa mensajes, analiza emociones, modera y responde.
- **Microservicio Backend**: recibe mensajes del frontend, consulta al NLP y devuelve la respuesta.
- **Sistema de cache Redis**: para acelerar respuestas de mensajes repetidos.
- **Base de datos MongoDB**: almacenamiento de las conversaciones de forma anonimizada.
- **Sistema de pruebas automáticas**: verificación de cada componente del sistema.
- **Despliegue automático**: mediante Docker Compose, listo para entornos de desarrollo o producción.

---

# Puesta en marcha de los servicios y validación del sistema

## 1. Construir la Imagen Base NLP

Primero, creamos la imagen optimizada que utilizará `nlp_service`:

```
docker build -t nlp_base_image -f nlp/Dockerfile.base nlp/
```
Esto instalará las librerías pesadas de NLP solo una vez.

Con la imagen base lista, levantamos todo el entorno:
```
docker-compose up -d --build
```
Este comando construye y levanta: backend, nlp_service, MongoDB y Redis.



## 2. Comprobar que los Contenedores están funcionando

Listamos los contenedores activos:
```
docker ps
```
Deberías ver algo similar:

| Container        | Status | Ports                       |
|------------------|--------|------------------------------|
| backend_chatbot  | Up     | 8000/tcp → 0.0.0.0:8000      |
| nlp_service      | Up     | 8001/tcp → 0.0.0.0:8001      |
| mongodb          | Up     | 27017/tcp                    |
| redis_cache      | Up     | 6379/tcp                     |


## 3. Ejecutar los Test Automáticos

### 1. Acceder al Contenedor del Servicio NLP
Entramos a la carpeta **nlp/**:
```
cd nlp
```

### 2. Lanzar todos los Tests de la carpeta tests/
Dentro de la carpeta lanzamos:
```
bash run_tests.sh
```
Esto ejecutará uno por uno todos los scripts de prueba:

* Test de cache Redis
* Test de limpieza de texto
* Test de procesamiento NLP
* Test de modelo de sentimiento
* Test de almacenamiento en MongoDB
* Test de anonimización de datos

Si todo va bien, verás un resumen final de tests pasados correctamente.

## 4. Realizar una Prueba Manual Rápida (Modo Consola)

### 1. Ejecutar Test Manual de Procesamiento de Texto

Dentro del contenedor nlp_service:
```
python -m tests.test_run
```
Esto comprobará que la función de preprocesamiento funciona correctamente.

### 2. Enviar un Mensaje de Prueba al API Backend

Desde tu máquina local, puedes usar curl para hacer una llamada directa:
```
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensaje_usuario":"Hoy me siento muy cansado y sin energía."}'
```
Si todo está configurado correctamente, recibirás una respuesta JSON parecida a:

```
{
  "estado_emocional": "negativo",
  "respuesta": "Parece que estás pasando por un momento difícil. Estoy aquí para escucharte. ¿Te gustaría contarme más?"
}
```

## 5. Comandos Útiles de Administración

### Detener todos los Contenedores
```
docker-compose down
```
### Reconstruir Contenedores si hay Cambios
```
docker-compose up -d --build
```

---

# Estructura de Archivos del Backend

Este proyecto está dividido en dos grandes servicios: **backend/** y **nlp/**, cada uno organizado de manera modular para facilitar el mantenimiento, la escalabilidad y las buenas prácticas en **FastAPI** y **procesamiento NLP**.

## Backend
Este directorio contiene el microservicio Backend API que expone los endpoints principales para el cliente (frontend o usuarios externos).
```
backend/
│── app/
│   ├── main.py             # Archivo principal que inicializa FastAPI y monta las rutas.
│   ├── routes/
│   │   ├── __init__.py      # Permite importar el módulo como paquete.
│   │   ├── chatbot.py       # Define la ruta POST /chat que conecta con el servicio NLP.
│   ├── models/
│   │   ├── __init__.py
│   │   ├── message.py       # Modelo Pydantic para validar el mensaje de entrada del usuario.
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp_service.py   # Funciones para comunicarse de manera asíncrona con el servicio NLP (vía HTTP).
│   ├── config.py            # Carga de variables de entorno (.env) y configuración general del proyecto.
│── .env                     # Variables sensibles de entorno (no subidas a repositorios públicos).
│── requirements.txt         # Dependencias necesarias para correr el servicio Backend.
```
Resumen:

- main.py → Arranca el servidor.
- routes/chatbot.py → Recibe el mensaje del usuario.
- models/message.py → Valida que el mensaje esté bien formado.
- services/nlp_service.py → Se comunica con el servicio de análisis NLP.
- config.py y .env → Gestionan las configuraciones del proyecto.

## Servicio NLP
Este directorio contiene el microservicio NLP Service responsable de:

* Procesar los mensajes de usuario.
* Realizar análisis de sentimientos.
* Moderar lenguaje ofensivo.
* Guardar interacciones.
* Cachear resultados.
```
nlp/
|── core/
|   |── __init__.py
|   |── cache.py             # Gestión de caché en Redis para evitar cálculos repetidos.
|   |── cleaner.py           # Funciones para limpiar el texto: eliminar URLs, símbolos, normalizar.
|   |── database.py          # Funciones para guardar interacciones en MongoDB de manera segura.
|   |── emotion_model.py     # Carga y ajuste del modelo de análisis emocional usando Transformers.
|   |── moderator.py         # Detección de palabras prohibidas o lenguaje ofensivo.
|   |── processor.py         # Procesamiento básico de texto: lematización, tokenización, stopwords.
|   |── response_generator.py# Lógica principal para generar respuestas seguras y empáticas.
|   |── security.py          # Funciones de anonimización de datos sensibles mediante SHA-256.
|── tests/
|   |── __init__.py
|   |── test_cache.py        # Pruebas automáticas para el sistema de caché Redis.
|   |── test_cleaner.py      # Pruebas automáticas para funciones de limpieza de texto.
|   |── test_emotion_model.py# Pruebas automáticas para análisis emocional del modelo NLP.
|   |── test_processor.py    # Pruebas de tokenización y procesamiento de texto.
|   |── test_response_save.py# Pruebas para guardar y verificar respuestas en MongoDB.
|   |── test_security.py     # Pruebas para validar funciones de anonimización.
|
|── __init__.py
|── .env                     # Variables sensibles específicas del servicio NLP.
|── app.py                   # API FastAPI que recibe mensajes y devuelve análisis emocional.
|── Dockerfile               # Construcción de la imagen final de producción para el servicio NLP.
|── Dockerfile.base          # Imagen base precompilada para acelerar la construcción de Docker.
|── requirements.txt         # Dependencias necesarias para el microservicio NLP.
|── run_tests.sh             # Script Bash para lanzar todos los tests automáticamente.
```
## Archivos Comunes
```
.gitignore
docker-compose.yml
README.md               # Documentación
```

## ¿Por qué esta estructura?

| Componente                    | Propósito |
|:-------------------------------|:----------|
| **routes/**                    | Define los endpoints de la API Backend de forma clara y desacoplada. |
| **models/**                    | Estandariza la entrada y salida de datos con validaciones automáticas. |
| **services/**                  | Separa la lógica de negocio para que las rutas estén limpias. |
| **core/** (NLP)                 | Reúne toda la funcionalidad del procesamiento de lenguaje natural: análisis, moderación, seguridad, respuesta, cacheo. |
| **tests/**                     | Facilita pruebas unitarias para cada componente clave de forma automática. |
| **config.py** y **.env**        | Centraliza toda la configuración y variables sensibles. |
| **Dockerfiles** y **docker-compose.yml** | Automatiza el despliegue de todos los servicios con ambientes controlados (producción y desarrollo). |

---

# Visualizar la Base de Datos de MongoDB

También puedes gestionar MongoDB directamente desde tu editor de código:

- Abre Visual Studio Code.
- Instala la extensión oficial **"MongoDB for VSCode"**.
- Pulsa en el icono de MongoDB que aparecerá en la barra lateral.
- Conecta utilizando la URI:
```
mongodb://localhost:27017
```
- Explora bases de datos y colecciones fácilmente desde el panel lateral de VSCode.
