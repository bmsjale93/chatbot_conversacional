# nlp/utils/extract_name.py
import re
import pandas as pd
import os
import unicodedata
import spacy
from typing import Optional

# ------------------ Lazy loading de spaCy ------------------

_spacy_model = None

def get_spacy_model():
    global _spacy_model
    if _spacy_model is None:
        try:
            _spacy_model = spacy.load("es_core_news_sm")
        except OSError as e:
            raise RuntimeError(
                "❌ Error cargando modelo de spaCy: asegúrate de tener 'es_core_news_sm' instalado."
            ) from e
    return _spacy_model

# ------------------ Ruta base ------------------

BASE_DIR = os.path.dirname(__file__)

# ------------------ Cargar nombres válidos ------------------

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

# ------------------ Normalización auxiliar ------------------

def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.lower().strip()

# ------------------ Función principal ------------------

def extraer_nombre(texto: str, modelo_spacy: Optional[spacy.language.Language] = None) -> str:
    texto = texto.strip()
    if not texto:
        return "Usuario"

    texto_normalizado = normalizar(texto)

    # -------- 1. Regex con frases comunes (más rápido) --------
    patrones = [
        r"(?:me llamo|soy|ll[aá]mame|puedes llamarme)\s+([A-ZÁÉÍÓÚÑa-záéíóúñü]+)",
        r"^([A-ZÁÉÍÓÚÑa-záéíóúñü]{2,})$"
    ]
    for patron in patrones:
        match = re.search(patron, texto, flags=re.IGNORECASE)
        if match:
            candidato = normalizar(match.group(1))
            if candidato in NOMBRES_VALIDOS:
                return candidato.capitalize()

    # -------- 2. Fallback: primer token válido --------
    tokens = texto.split()
    if tokens:
        primer_token = normalizar(tokens[0])
        if primer_token in NOMBRES_VALIDOS:
            return primer_token.capitalize()
        # Si sólo hay una palabra, devolverla directamente
        if len(tokens) == 1:
            return tokens[0].capitalize()

    # -------- 3. NER con spaCy (último recurso) --------
    if modelo_spacy is None:
        modelo_spacy = get_spacy_model()

    try:
        doc = modelo_spacy(texto)
        for ent in doc.ents:
            if ent.label_ == "PER":
                candidato = ent.text.strip().split()[0].lower()
                if candidato in NOMBRES_VALIDOS:
                    return candidato.capitalize()
    except Exception as e:
        print(f"⚠️ Error usando spaCy: {e}")

    return "Usuario"
