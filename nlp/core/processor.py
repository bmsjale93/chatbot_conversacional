# Procesamiento de lenguaje natural
import spacy
# Importamos NLTK y su módulo de stopwords
import nltk
from nltk.corpus import stopwords
from core.cleaner import limpiar_texto

# Inicializamos las stopwords de NLTK
try:
    _ = stopwords.words('spanish')
except LookupError:
    # Si no están descargadas, las descargamos
    nltk.download('stopwords')

# Cargamos el modelo de spaCy en español
nlp = spacy.load("es_core_news_sm")

# Función para preprocesar el texto
def preprocesar_texto(texto: str) -> list:
    """
    Limpia el texto, lematiza las palabras, elimina stopwords y puntuación,
    y devuelve una lista de tokens útiles.
    """
    texto_limpio = limpiar_texto(texto)  # Limpieza inicial del texto
    doc = nlp(texto_limpio)  # Procesamos el texto con spaCy

    # Extraemos los lemas de las palabras, ignorando stopwords y signos de puntuación
    tokens = [
        token.lemma_ for token in doc if not token.is_stop and not token.is_punct
    ]

    # Conjunto de stopwords en español
    stopwords_nltk = set(stopwords.words('spanish'))

    # Stopwords personalizadas adicionales
    stopwords_personalizadas = {"últimamente", "totalmente"}

    # Filtramos los tokens para eliminar stopwords de NLTK y personalizadas
    tokens_filtrados = [
        t for t in tokens
        if t not in stopwords_nltk and t not in stopwords_personalizadas
    ]

    return tokens_filtrados
