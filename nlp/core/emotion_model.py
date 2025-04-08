# Importamos el pipeline de Hugging Face para análisis de sentimientos
from transformers import pipeline

# Inicializamos el modelo de análisis de sentimiento
modelo = pipeline(
    task="sentiment-analysis",
    model="pysentimiento/robertuito-sentiment-analysis"
)

# Función para ajustar manualmente el resultado del modelo
def ajustar_emocion(texto: str, resultado_modelo: dict) -> dict:
    """
    Aplica reglas personalizadas sobre el resultado del modelo para mejorar la interpretación.
    """
    label = resultado_modelo["label"]  # Resultado del modelo: POS, NEU o NEG
    score = resultado_modelo["score"]

    # Si el resultado es negativo pero poco confiable y el texto contiene "no sé", cambiamos a neutro
    if label == "NEG" and score < 0.85 and "no sé" in texto.lower():
        label = "NEU"

    # Diccionario para traducir las etiquetas
    emociones = {
        "POS": "Positivo",
        "NEU": "Neutro",
        "NEG": "Negativo"
    }

    return {
        "estado_emocional": emociones.get(label, "desconocido"),
        "confianza": f"{round(score * 100, 1)}%"
    }

# Función principal para analizar el sentimiento del texto
def analizar_sentimiento(texto: str) -> dict:
    """
    Analiza el sentimiento de un texto y devuelve el estado emocional y la confianza.
    """
    # Si el texto está vacío o sólo tiene espacios, devolvemos desconocido
    if not texto.strip():
        return {
            "estado_emocional": "desconocido",
            "confianza": "0%"
        }

    try:
        # Analizamos el sentimiento y ajustamos el resultado
        resultado = modelo(texto)[0]
        return ajustar_emocion(texto, resultado)
    except Exception as e:
        # Si ocurre un error, devolvemos un estado de error
        return {
            "estado_emocional": "error",
            "confianza": "0%",
            "detalle": str(e)
        }
