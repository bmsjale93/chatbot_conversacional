import os
from typing import Set

# Ruta al archivo que contiene las palabras prohibidas
RUTA_LISTA: str = os.path.join(os.path.dirname(__file__), "palabras_prohibidas.txt")

def cargar_palabras_prohibidas() -> Set[str]:
    """Carga palabras ofensivas o peligrosas desde archivo de texto."""
    try:
        with open(RUTA_LISTA, "r", encoding="utf-8") as f:
            return {line.strip().casefold() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Archivo de palabras prohibidas no encontrado en {RUTA_LISTA}. Se cargará lista vacía.")
        return set()
    except Exception as e:
        print(f"Error cargando palabras prohibidas: {str(e)}")
        return set()

# Lista cargada una sola vez al inicio
PALABRAS_PROHIBIDAS: Set[str] = cargar_palabras_prohibidas()

def contiene_lenguaje_inapropiado(texto: str) -> bool:
    """Verifica si el texto contiene alguna palabra prohibida."""
    if not texto:
        return False
    texto_limpio = texto.strip().casefold()
    return any(palabra in texto_limpio for palabra in PALABRAS_PROHIBIDAS)
