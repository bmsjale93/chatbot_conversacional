import unicodedata
import re
from typing import Literal
from sentence_transformers import SentenceTransformer, util

# ------------------ Modelo de similitud semántica ------------------
modelo_similitud = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# ------------------ Expresiones Extendidas ------------------
EXPRESIONES_AFIRMATIVAS = [
    "sí", "si", "claro", "vale", "de acuerdo", "afirmativo", "por supuesto", "sin duda", "perfecto",
    "genial", "está bien", "acepto", "continuar", "adelante", "vamos", "venga", "sí quiero", "seguro",
    "me parece bien", "estoy listo", "ok", "sigamos", "sí, vamos a seguir", "continúa", "quiero seguir",
    "sí, por favor", "dale", "acepto continuar", "continuemos", "por mi parte sí", "sin problema",
    "vale, sigamos", "estoy de acuerdo", "sigamos por favor", "quiero continuar",
    "sí, me he sentido triste", "sí, me he sentido muy triste", "sí, últimamente me he sentido triste"
]

EXPRESIONES_NEGATIVAS = [
    "no", "prefiero no", "mejor no", "rechazo", "no quiero", "no deseo", "no gracias", "no por ahora",
    "nunca", "no estoy seguro", "quizá no", "no quiero seguir", "no, gracias", "ahora no", "negativo",
    "paso", "no quiero continuar", "prefiero parar", "quiero parar", "quiero terminar", "no sigamos",
    "quiero dejarlo", "dejarlo", "detener", "finalizar", "terminar conversación", "basta",
    "prefiero no seguir", "no deseo continuar", "cancela", "ya no quiero", "deten esto", "me retiro", 
    "no me he sentido bien"
]

# ------------------ Utilidades opcionales ------------------
DEBUG = True

def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto.lower().strip()

# ------------------ Detección de intención ------------------
def detectar_intencion(texto_usuario: str) -> Literal["afirmativo", "negativo", "desconocido"]:
    if not texto_usuario:
        return "desconocido"

    texto_normalizado = normalizar_texto(texto_usuario)

    if DEBUG:
        print(f"[DEBUG] Texto original: {texto_usuario}")
        print(f"[DEBUG] Texto normalizado: {texto_normalizado}")

    # Paso 1: Detección exacta
    if texto_normalizado in EXPRESIONES_AFIRMATIVAS:
        return "afirmativo"
    if texto_normalizado in EXPRESIONES_NEGATIVAS:
        return "negativo"

    # Paso 2: Similitud semántica
    emb_usuario = modelo_similitud.encode(texto_normalizado, convert_to_tensor=True)
    emb_afirmativas = modelo_similitud.encode(EXPRESIONES_AFIRMATIVAS, convert_to_tensor=True)
    emb_negativas = modelo_similitud.encode(EXPRESIONES_NEGATIVAS, convert_to_tensor=True)

    sim_afirmativa = util.pytorch_cos_sim(emb_usuario, emb_afirmativas).max().item()
    sim_negativa = util.pytorch_cos_sim(emb_usuario, emb_negativas).max().item()

    if DEBUG:
        print(f"[DEBUG] Similitud afirmativa: {sim_afirmativa:.4f}")
        print(f"[DEBUG] Similitud negativa: {sim_negativa:.4f}")

    if sim_afirmativa > 0.7 and sim_afirmativa > sim_negativa:
        return "afirmativo"
    elif sim_negativa > 0.7 and sim_negativa > sim_afirmativa:
        return "negativo"

    return "desconocido"
