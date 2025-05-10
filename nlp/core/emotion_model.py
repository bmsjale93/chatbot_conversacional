from typing import Dict
import unicodedata
import re
import difflib
from pysentimiento import create_analyzer

# Emociones compatibles con el sistema
EMOCIONES_VALIDAS = [
    "alegría", "amor", "enojo", "miedo", "tristeza", "sorpresa", "culpa",
    "vergüenza", "frustración", "ansiedad", "agotamiento", "soledad",
    "esperanza", "indiferencia", "preocupación", "confusión", "neutral", "anhedonia"
]

# Traducción desde emociones detectadas por pysentimiento
TRADUCCION_PYSENTIMIENTO = {
    "joy": "alegría",
    "sadness": "tristeza",
    "anger": "enojo",
    "fear": "miedo",
    "surprise": "sorpresa",
    "disgust": "culpa",
    "others": "neutral"
}

# Lista normalizada para comparación
EMOCIONES_VALIDAS_NORMALIZADAS = [
    unicodedata.normalize("NFKD", e).encode("ascii", "ignore").decode("utf-8").lower()
    for e in EMOCIONES_VALIDAS
]

# Carga del modelo de emociones
try:
    print("Cargando modelo pysentimiento (emotion, lang='es')...")
    modelo = create_analyzer(task="emotion", lang="es")
    print("Modelo cargado correctamente.")
except Exception as e:
    import traceback
    print("Error al cargar el modelo:")
    traceback.print_exc()
    modelo = None


def limpiar_texto_emocion(texto: str) -> str:
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\s]", "", texto)
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")


def fallback_por_similitud(emocion_limpia: str) -> str:
    coincidencias = difflib.get_close_matches(emocion_limpia, EMOCIONES_VALIDAS_NORMALIZADAS, n=1, cutoff=0.8)
    if coincidencias:
        index = EMOCIONES_VALIDAS_NORMALIZADAS.index(coincidencias[0])
        return EMOCIONES_VALIDAS[index]
    return "desconocido"


def analizar_sentimiento(texto: str) -> Dict[str, str]:
    if not texto.strip():
        return {
            "estado_emocional": "desconocido",
            "confianza": "0%"
        }

    if modelo is None:
        return {
            "estado_emocional": "error",
            "confianza": "0%",
            "detalle": "Modelo no cargado correctamente."
        }

    try:
        resultado = modelo.predict(texto)
        print(f"[DEBUG] Resultado del modelo: {resultado}")

        emocion_detectada = resultado.output.strip().lower()
        confianza_raw = resultado.probas.get(emocion_detectada, 0.0)
        confianza = f"{round(confianza_raw * 100)}%"

        emocion_traducida = TRADUCCION_PYSENTIMIENTO.get(emocion_detectada, emocion_detectada)
        emocion_limpia = limpiar_texto_emocion(emocion_traducida)

        if emocion_limpia in EMOCIONES_VALIDAS_NORMALIZADAS:
            index = EMOCIONES_VALIDAS_NORMALIZADAS.index(emocion_limpia)
            emocion_final = EMOCIONES_VALIDAS[index]
        else:
            emocion_final = fallback_por_similitud(emocion_limpia)

        return {
            "estado_emocional": emocion_final,
            "confianza": confianza
        }

    except Exception as e:
        return {
            "estado_emocional": "error",
            "confianza": "0%",
            "detalle": str(e)
        }