from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime, timezone
from typing import Optional
import os
import logging

from fpdf import FPDF
from core.security import anonimizar_texto
from core.emotion_model import analizar_sentimiento
from core.score_manager import obtener_puntuaciones

# Configuración del logger
logger = logging.getLogger(__name__)

# Conexión a MongoDB
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
cliente = MongoClient(MONGO_URL)
db = cliente.get_database("chatbot")
conversaciones = db.get_collection("historial")

# ------------------------ FUNCIONES PRINCIPALES ------------------------

def guardar_interaccion(
    texto: str,
    respuesta: str,
    emocion: str,
    session_id: str,
    guardar_texto_original: bool = False
) -> None:
    doc = {
        "session_id": session_id,
        "mensaje_hash": anonimizar_texto(texto),
        "respuesta_sistema": respuesta,
        "emocion": emocion.lower(),
        "timestamp": datetime.now(timezone.utc)
    }

    if guardar_texto_original:
        doc["mensaje_usuario"] = texto

    try:
        conversaciones.insert_one(doc)
    except PyMongoError as e:
        logger.error(f"❌ Error guardando interacción (simple): {e}")

def guardar_interaccion_completa(
    session_id: str,
    estado: str,
    pregunta: str,
    respuesta_usuario: str,
    puntuacion: Optional[int] = None,
    emocion: Optional[str] = None,
    confianza: Optional[str] = None
) -> None:
    if emocion is None or confianza is None:
        resultado_emocional = analizar_sentimiento(respuesta_usuario)
        emocion = resultado_emocional.get("estado_emocional", "pendiente").lower()
        confianza = resultado_emocional.get("confianza", "0%")

    if puntuacion is None:
        puntuaciones = obtener_puntuaciones(session_id)
        tipo_estado_a_clave = {
            "preguntar_frecuencia": "frecuencia",
            "preguntar_duracion": "duracion",
            "intensidad_tristeza": "intensidad",
            "preguntar_desesperanza": "desesperanza",
            "preguntar_inutilidad": "inutilidad",
            "preguntar_ideacion_suicida": "ideacion",
            "preguntar_anhedonia": "anhedonia"
        }
        tipo = tipo_estado_a_clave.get(estado)
        puntuacion = puntuaciones.get(tipo, 0) if tipo else 0

    doc = {
        "session_id": session_id,
        "estado": estado,
        "pregunta": pregunta,
        "respuesta_usuario": respuesta_usuario,
        "emocion": emocion,
        "confianza_emocion": confianza,
        "puntuacion": puntuacion,
        "timestamp": datetime.now(timezone.utc)
    }

    try:
        conversaciones.insert_one(doc)
    except PyMongoError as e:
        logger.error(f"❌ Error guardando interacción completa: {e}")

def obtener_historial_conversacion(session_id: str) -> list:
    from pymongo import ASCENDING
    cursor = conversaciones.find({"session_id": session_id}).sort("timestamp", ASCENDING)

    historial = []
    for doc in cursor:
        if "pregunta" in doc:
            historial.append({"role": "assistant", "content": doc["pregunta"]})
        if "respuesta_usuario" in doc:
            historial.append({"role": "user", "content": doc["respuesta_usuario"]})
    return historial

def generar_pdf_informe(session_id: str, ruta_salida: str = "informe_emocional.pdf") -> Optional[str]:
    try:
        cursor = conversaciones.find({"session_id": session_id}).sort("timestamp", 1)
        registros = list(cursor)

        if not registros:
            logger.warning(f"No se encontraron datos para la sesión: {session_id}")
            return None

        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, "Informe de Evaluación Emocional", ln=True, align="C")
                self.ln(5)

            def chapter_title(self, num, title):
                self.set_font("Arial", "B", 11)
                self.set_fill_color(240, 240, 240)
                self.cell(0, 8, f"{num}. {title}", ln=True, fill=True)
                self.ln(1)

            def chapter_body(self, body):
                self.set_font("Arial", "", 10)
                self.multi_cell(0, 8, body)
                self.ln()

        pdf = PDF()
        pdf.add_page()

        for idx, reg in enumerate(registros, 1):
            pregunta = reg.get("pregunta", "")
            respuesta = reg.get("respuesta_usuario", "")
            emocion = reg.get("emocion", "")
            confianza = reg.get("confianza_emocion", "")
            puntuacion = reg.get("puntuacion", "")
            fecha = reg.get("timestamp", "").strftime("%Y-%m-%d %H:%M") if reg.get("timestamp") else "N/A"

            pdf.chapter_title(idx, pregunta)
            cuerpo = f"Respuesta: {respuesta}\nEmoción detectada: {emocion} ({confianza})\nPuntuación: {puntuacion}\nFecha: {fecha}"
            pdf.chapter_body(cuerpo)

        pdf.output(ruta_salida)
        logger.info(f"📄 Informe PDF generado correctamente: {ruta_salida}")
        return ruta_salida

    except Exception as e:
        logger.error(f"❌ Error generando PDF: {e}")
        return None
