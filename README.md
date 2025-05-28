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

## Tiempo para Levantar Contenedores:

- **15-20 minutos**

## Tecnologías utilizadas en el Proyecto

| Tecnología                        | Propósito                                                                 |
|:----------------------------------|:--------------------------------------------------------------------------|
| **FastAPI**                       | Backend para API REST, altamente eficiente y asíncrono                    |
| **Gradio**                        | Frontend interactivo para el usuario con interfaz conversacional          |
| **Docker & Docker Compose**       | Contenerización completa y orquestación de servicios                      |
| **MongoDB**                       | Base de datos NoSQL para registrar historial de conversación y evaluaciones |
| **Redis**                         | Almacenamiento en caché para respuestas y estados de conversación         |
| **Transformers + PySentimiento** | Análisis emocional usando modelos entrenados en español                   |
| **spaCy**                         | Procesamiento lingüístico para extracción y limpieza de texto             |
| **Sentence Transformers**         | Detección de intención mediante similitud semántica                       |
| **FPDF**                          | Generación automática de informes emocionales en PDF                      |
| **pytest + scripts**              | Pruebas unitarias y de integración para garantizar la robustez del sistema |

---

## ¿Qué incluye este proyecto?

- **Frontend Gradio**: interfaz visual con historial, sugerencias y reinicio de conversación.
- **Microservicio NLP**: gestiona flujo conversacional, analiza emociones, modera lenguaje e imprime informes PDF.
- **Microservicio Backend**: puente entre frontend y NLP; controla sesiones y persistencia.
- **Análisis emocional en español**: clasificación empática basada en sentimientos reconocibles.
- **Gestión de intención y ambigüedad**: comprensión de respuestas afirmativas, negativas y neutras.
- **Almacenamiento optimizado**: MongoDB para historial completo, Redis para sesiones, emociones y puntuaciones.
- **Evaluación emocional clínica**: basada en criterios similares al BDI-II con puntuaciones, intensidad y resumen.
- **Generación de PDF descargable**: informe emocional completo por sesión, accesible desde cualquier interfaz.
- **Despliegue con Docker Compose**: configurado para levantar todo el sistema con un único comando.

---

# Puesta en marcha de los servicios y validación del sistema

## 1. Levantar todos los servicios

Para construir la imagen base del NLP y lanzar todos los contenedores correctamente configurados, simplemente ejecuta desde la raíz del proyecto:

```bash
./reset_and_run.sh
```

Este script realiza automáticamente los siguientes pasos:

- Detiene y elimina todos los contenedores existentes.
- Elimina las imágenes antiguas para forzar una reconstrucción limpia.
- Construye la imagen base nlp-base desde nlp/Dockerfile.base.
- Levanta todos los servicios definidos en docker-compose.yml, incluyendo:
  - Backend (FastAPI)
  - Servicio NLP (análisis emocional)
  - Frontend (Gradio)
  - MongoDB
  - Redis

**Asegúrate de que el script tenga permisos de ejecución.** Puedes asignarlos con:
```bash
chmod +x reset_and_run.sh
```

## 2. Comprobar que los contenedores están funcionando
Puedes verificar que todos los contenedores estén activos con:
```bash
docker ps
```
Deberías ver una salida similar a esta:

| Contenedor        | Estado | Puertos                  |
|-------------------|--------|---------------------------|
| backend_chatbot   | Up     | 8000 → 0.0.0.0:8000       |
| nlp_service       | Up     | 8001 → 0.0.0.0:8001       |
| frontend_gradio   | Up     | 7860 → 0.0.0.0:7860       |
| mongodb           | Up     | 27017/tcp                 |
| redis_cache       | Up     | 6379/tcp                  |


## 3. Limpiar la base de datos

Si deseas eliminar todas las conversaciones y reiniciar el sistema desde cero, ejecuta el siguiente comando desde la raíz del proyecto:
```bash
python limpiar_base.py
```
Este script conecta con MongoDB y elimina todos los documentos de todas las colecciones dentro de la base de datos chatbot.

## 4. Variables de entorno necesarias

Asegúrate de que cada servicio tenga configurado su archivo `.env` correspondiente:


### backend/.env
```
DATABASE_URL=mongodb://db:27017/chatbot
SECRET_KEY=supersecreta123
NLP_GESTIONAR_URL=http://nlp:8001/gestionar
```
### nlp/.env
```
DATABASE_URL=mongodb://db:27017/chatbot
REDIS_HOST=redis
REDIS_PORT=6379
```

### frontend/.env
```
BACKEND_URL=http://backend:8000/api/chat
```

---

# Endpoints disponibles

### Backend API (`http://localhost:8000`)

- `GET /`  
  Verifica que el backend está activo.

- `POST /api/chat`  
  Envía un mensaje del usuario y recibe una respuesta emocional estructurada.

- `GET /api/chat/historial?session_id=...`  
  Recupera el historial de conversación de una sesión específica.

---

### NLP Service (`http://localhost:8001`)

- `GET /`  
  Verifica que el servicio NLP está activo.

- `POST /analyze`  
  Analiza emocionalmente un mensaje individual.

- `POST /gestionar`  
  Procesa el mensaje dentro del flujo conversacional completo y devuelve la respuesta correspondiente.

---

# Guía de desarrollo o contribución

¿Te gustaría mejorar este proyecto? ¡Las contribuciones son bienvenidas!

Sigue estos pasos para colaborar:

1. Haz un fork del repositorio.
2. Crea una nueva rama para tu funcionalidad o mejora:

```bash
git checkout -b mejora-caracteristica
```

3. Realiza tus cambios y haz un commit:

```
git commit -m "Añadir nueva característica"
```

4. Sube los cambios a tu fork:
```
git push origin mejora-caracteristica
```

5. Abre un Pull Request describiendo detalladamente los cambios realizados.


---

### Proyecto desarrollado por Alejandro Delgado entre líneas de código, ideas persistentes... y cantidades sospechosas de café.