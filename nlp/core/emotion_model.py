# nlp/core/emotion_model.py
from transformers import pipeline
from typing import Dict

# Diccionario para traducir las etiquetas
MAPEO_EMOCIONES = {
    "POS": "Positivo",
    "NEU": "Neutro",
    "NEG": "Negativo"
}

# Modelo NLP de HuggingFace (inicialización lazy)
modelo = None

def cargar_modelo():
    global modelo
    if modelo is None:
        modelo = pipeline(
            task="sentiment-analysis",
            model="pysentimiento/robertuito-sentiment-analysis"
        )


def ajustar_emocion(texto: str, resultado_modelo: dict) -> Dict[str, str]:
    """
    Ajusta manualmente la emoción basada en reglas personalizadas.
    """
    label = resultado_modelo.get("label", "NEU")
    score = resultado_modelo.get("score", 0)

    # Reglas específicas
    if label == "NEG" and score < 0.85 and "no sé" in texto.lower():
        label = "NEU"

    return {
        "estado_emocional": MAPEO_EMOCIONES.get(label, "desconocido"),
        "confianza": f"{round(score * 100, 1)}%"
    }


def analizar_sentimiento(texto: str) -> Dict[str, str]:
    """
    Analiza el sentimiento de un texto y devuelve el estado emocional y la confianza.
    """
    if not texto.strip():
        return {
            "estado_emocional": "desconocido",
            "confianza": "0%"
        }

    try:
        cargar_modelo()
        resultado = modelo(texto)[0]
        return ajustar_emocion(texto, resultado)
    except Exception as e:
        return {
            "estado_emocional": "error",
            "confianza": "0%",
            "detalle": str(e)
        }
