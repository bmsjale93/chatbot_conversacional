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
    "sí, me he sentido triste", "sí, me he sentido muy triste", "sí, últimamente me he sentido triste",
    "ya no disfruto", "he dejado de disfrutar", "he perdido interés", "me cuesta disfrutar",
    "no encuentro placer", "no me interesa lo mismo", "no me apetece nada",
    "he notado cambios", "he notado que", "como peor", "como diferente", "ha cambiado mi apetito"
]

EXPRESIONES_NEGATIVAS = [
    "no", "prefiero no", "mejor no", "rechazo", "no quiero", "no deseo", "no gracias", "no por ahora",
    "nunca", "no estoy seguro", "quizá no", "no quiero seguir", "no, gracias", "ahora no", "negativo",
    "paso", "no quiero continuar", "prefiero parar", "quiero parar", "quiero terminar", "no sigamos",
    "quiero dejarlo", "dejarlo", "detener", "finalizar", "terminar conversación", "basta",
    "prefiero no seguir", "no deseo continuar", "cancela", "ya no quiero", "deten esto", "me retiro", 
    "no me he sentido bien", "sigo disfrutando", "no he perdido interés", "disfruto igual"
]

# ------------------ Utilidades ------------------
DEBUG = True

def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto.lower().strip()

def contiene_frase_completa(texto: str, frase: str) -> bool:
    return re.search(rf"\b{re.escape(frase)}\b", texto) is not None

# ------------------ Detección de intención ------------------
def detectar_intencion(texto_usuario: str) -> Literal["afirmativo", "negativo", "desconocido"]:
    if not texto_usuario:
        return "desconocido"

    texto_normalizado = normalizar_texto(texto_usuario)

    if DEBUG:
        print(f"[DEBUG] Texto original: {texto_usuario}")
        print(f"[DEBUG] Texto normalizado: {texto_normalizado}")

    # Paso 1: Coincidencia exacta
    if texto_normalizado in EXPRESIONES_AFIRMATIVAS:
        return "afirmativo"
    if texto_normalizado in EXPRESIONES_NEGATIVAS:
        return "negativo"

    # Paso 2: Coincidencia por inclusión (priorizar afirmativas)
    for frase in EXPRESIONES_AFIRMATIVAS:
        if contiene_frase_completa(texto_normalizado, frase):
            return "afirmativo"
    for frase in EXPRESIONES_NEGATIVAS:
        if contiene_frase_completa(texto_normalizado, frase):
            return "negativo"

    # Paso 3: Similaridad semántica
    emb_usuario = modelo_similitud.encode(texto_normalizado, convert_to_tensor=True)
    emb_afirmativas = modelo_similitud.encode(EXPRESIONES_AFIRMATIVAS, convert_to_tensor=True)
    emb_negativas = modelo_similitud.encode(EXPRESIONES_NEGATIVAS, convert_to_tensor=True)

    sim_afirmativa = util.pytorch_cos_sim(emb_usuario, emb_afirmativas).max().item()
    sim_negativa = util.pytorch_cos_sim(emb_usuario, emb_negativas).max().item()

    if DEBUG:
        print(f"[DEBUG] Similitud afirmativa: {sim_afirmativa:.4f}")
        print(f"[DEBUG] Similitud negativa: {sim_negativa:.4f}")

    if sim_afirmativa > sim_negativa and sim_afirmativa > 0.70:
        return "afirmativo"
    elif sim_negativa > sim_afirmativa and sim_negativa > 0.70:
        return "negativo"

    return "desconocido"
