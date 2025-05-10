import spacy
import nltk
from nltk.corpus import stopwords
from typing import List
from core.cleaner import limpiar_texto

# Stopwords personalizadas (se combinan con las de NLTK)
def cargar_stopwords() -> set:
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")

    stopwords_nltk = set(stopwords.words("spanish"))
    stopwords_personalizadas = {"últimamente", "totalmente"}
    return stopwords_nltk.union(stopwords_personalizadas)

STOPWORDS_TOTALES = cargar_stopwords()

# Carga diferida del modelo de spaCy para rendimiento
_spacy_model = None

def get_spacy_model():
    global _spacy_model
    if _spacy_model is None:
        try:
            _spacy_model = spacy.load("es_core_news_sm", disable=["ner", "parser"])
        except OSError as e:
            raise RuntimeError(
                "Error cargando modelo de spaCy. Asegúrate de tener 'es_core_news_sm' instalado."
            ) from e
    return _spacy_model

# Preprocesamiento completo del texto
def preprocesar_texto(texto: str) -> List[str]:
    """
    Limpia el texto, lematiza palabras, elimina stopwords y puntuación,
    y devuelve una lista de tokens útiles.
    """
    texto_limpio = limpiar_texto(texto)
    nlp = get_spacy_model()
    doc = nlp(texto_limpio)

    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct
    ]

    return [t for t in tokens if t not in STOPWORDS_TOTALES]
