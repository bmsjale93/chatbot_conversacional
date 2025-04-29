import os
from typing import Set

# Definimos la ruta al archivo de palabras prohibidas
RUTA_LISTA: str = os.path.join(os.path.dirname(
    __file__), "palabras_prohibidas.txt")


def cargar_palabras_prohibidas() -> Set[str]:
    """
    Carga las palabras ofensivas o peligrosas desde un archivo de texto,
    devolviendo un conjunto de palabras en minúsculas.
    """
    try:
        with open(RUTA_LISTA, "r", encoding="utf-8") as f:
            palabras = {line.strip().casefold() for line in f if line.strip()}
        return palabras
    except FileNotFoundError:
        print(
            f"⚠️ Archivo de palabras prohibidas no encontrado en {RUTA_LISTA}. Se cargará lista vacía.")
        return set()
    except Exception as e:
        print(f"⚠️ Error cargando palabras prohibidas: {str(e)}")
        return set()


# Cargamos las palabras prohibidas una sola vez al iniciar
PALABRAS_PROHIBIDAS: Set[str] = cargar_palabras_prohibidas()


def contiene_lenguaje_inapropiado(texto: str) -> bool:
    """
    Verifica si el texto contiene alguna palabra ofensiva de la lista cargada.
    """
    if not texto:
        return False

    texto_limpio = texto.strip().casefold()
    return any(palabra in texto_limpio for palabra in PALABRAS_PROHIBIDAS)
