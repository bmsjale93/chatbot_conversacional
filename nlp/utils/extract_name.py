# nlp/utils/extract_name.py
import re
import pandas as pd
import spacy
import os

# Carga modelo de spaCy
nlp_spacy = spacy.load("es_core_news_sm")

# Ruta base al directorio actual (por si se ejecuta desde otro contexto)
BASE_DIR = os.path.dirname(__file__)

# ------------------ Cargar y unir nombres válidos ------------------
def cargar_nombres_validos() -> set:
    try:
        df_female = pd.read_csv(os.path.join(BASE_DIR, "female_names.csv"))
        df_male = pd.read_csv(os.path.join(BASE_DIR, "male_names.csv"))

        nombres_f = df_female["name"].astype(str).str.strip().str.lower()
        nombres_m = df_male["name"].astype(str).str.strip().str.lower()

        return set(nombres_f).union(set(nombres_m))
    except Exception as e:
        print(f"❌ Error cargando nombres válidos: {e}")
        return set()


NOMBRES_VALIDOS = cargar_nombres_validos()

# ------------------ Función principal ------------------


def extraer_nombre(texto: str) -> str:
    texto = texto.strip()

    # -------- 1. NER con spaCy --------
    doc = nlp_spacy(texto)
    for ent in doc.ents:
        if ent.label_ == "PER":
            candidato = ent.text.strip().split()[0].lower()
            if candidato in NOMBRES_VALIDOS:
                return candidato.capitalize()

    # -------- 2. Regex por frases típicas --------
    patrones = [
        r"(?:me llamo|soy|ll[aá]mame|puedes llamarme)\s+([A-ZÁÉÍÓÚÑa-záéíóúñü]+)",
        r"^([A-ZÁÉÍÓÚÑa-záéíóúñü]{2,})$"
    ]
    for patron in patrones:
        match = re.search(patron, texto, flags=re.IGNORECASE)
        if match:
            candidato = match.group(1).strip().lower()
            if candidato in NOMBRES_VALIDOS:
                return candidato.capitalize()

    # -------- 3. Fallback: Primer token capitalizado --------
    tokens = texto.split()
    if tokens:
        primer_token = tokens[0].lower()
        if primer_token in NOMBRES_VALIDOS:
            return primer_token.capitalize()
        return tokens[0].capitalize()

    return "Usuario"
