import os

# Definimos la ruta al archivo de palabras prohibidas
RUTA_LISTA = os.path.join(os.path.dirname(
    __file__), "../../palabras_prohibidas.txt")

# Función para cargar las palabras prohibidas desde un archivo de texto
def cargar_palabras_prohibidas() -> set:
    """
    Carga las palabras ofensivas o peligrosas desde un archivo de texto,
    devolviendo un conjunto (set) de palabras en minúsculas.
    """
    try:
        with open(RUTA_LISTA, "r", encoding="utf-8") as f:
            palabras = {line.strip().lower() for line in f if line.strip()}
        return palabras
    except FileNotFoundError:
        # Si no se encuentra el archivo, devolvemos un conjunto vacío
        return set()


# Cargamos las palabras prohibidas una sola vez al iniciar
PALABRAS_PROHIBIDAS = cargar_palabras_prohibidas()

# Función para verificar si un texto contiene palabras ofensivas
def contiene_lenguaje_inapropiado(texto: str) -> bool:
    """
    Verifica si el texto contiene alguna palabra ofensiva de la lista cargada.
    """
    texto_limpio = texto.lower()
    return any(palabra in texto_limpio for palabra in PALABRAS_PROHIBIDAS)
