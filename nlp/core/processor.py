# Procesamiento de lenguaje natural
import spacy
import nltk
from nltk.corpus import stopwords
from typing import List
from core.cleaner import limpiar_texto

# Inicializamos stopwords de NLTK
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

stopwords_nltk = set(stopwords.words("spanish"))
stopwords_personalizadas = {"últimamente", "totalmente"}
STOPWORDS_TOTALES = stopwords_nltk.union(stopwords_personalizadas)

# Cargamos modelo de spaCy
try:
    nlp = spacy.load("es_core_news_sm")
except OSError as e:
    raise RuntimeError(
        "❌ Error cargando modelo de spaCy: asegúrate de tener 'es_core_news_sm' instalado.") from e


def preprocesar_texto(texto: str) -> List[str]:
    """
    Limpia el texto, lematiza palabras, elimina stopwords y puntuación,
    y devuelve una lista de tokens útiles.
    """
    texto_limpio = limpiar_texto(texto)
    doc = nlp(texto_limpio)

    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct
    ]

    # Filtramos stopwords extendidas
    tokens_filtrados = [t for t in tokens if t not in STOPWORDS_TOTALES]

    return tokens_filtrados
