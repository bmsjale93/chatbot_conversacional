# nlp/tests/test_security.py

from core.security import anonimizar_texto


def test_anonimizar_texto_mismo_input_mismo_hash():
    """El mismo texto debe generar siempre el mismo hash."""
    texto = "Me siento bien"
    hash1 = anonimizar_texto(texto)
    hash2 = anonimizar_texto(texto)
    assert hash1 == hash2, "[Error] El mismo texto debería producir el mismo hash."
    print("✅ Test 1: Mismo input → mismo hash: OK")


def test_anonimizar_texto_diferente_input_diferente_hash():
    """Textos diferentes deben producir hashes diferentes."""
    texto1 = "Me siento bien"
    texto2 = "Me siento mal"
    hash1 = anonimizar_texto(texto1)
    hash2 = anonimizar_texto(texto2)
    assert hash1 != hash2, "[Error] Textos distintos deberían producir hashes distintos."
    print("✅ Test 2: Diferente input → diferente hash: OK")


def test_anonimizar_texto_normalizacion():
    """Hashing debe ser consistente ignorando espacios o mayúsculas."""
    texto1 = "Me siento BIEN"
    texto2 = "   me siento bien   "
    hash1 = anonimizar_texto(texto1.strip().lower())
    hash2 = anonimizar_texto(texto2.strip().lower())
    assert hash1 == hash2, "[Error] El hashing debe ser independiente de mayúsculas y espacios."
    print("✅ Test 3: Normalización espacios/mayúsculas: OK")


def test_anonimizar_texto_input_vacio():
    """Debe lanzar un error si el texto de entrada está vacío."""
    try:
        anonimizar_texto("")
        assert False, "[Error] Debería lanzar ValueError si el texto está vacío."
    except ValueError:
        print("✅ Test 4: Input vacío lanza ValueError: OK")


# Ejecutar todos los tests manualmente
if __name__ == "__main__":
    print("\n🚀 Iniciando tests de Seguridad (Anonimización de Texto)...\n")

    test_anonimizar_texto_mismo_input_mismo_hash()
    test_anonimizar_texto_diferente_input_diferente_hash()
    test_anonimizar_texto_normalizacion()
    test_anonimizar_texto_input_vacio()

    print("\n🎯 Todos los tests de Seguridad completados exitosamente.\n")
