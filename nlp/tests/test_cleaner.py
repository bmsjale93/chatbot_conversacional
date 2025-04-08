# nlp/tests/test_cleaner.py

from core.cleaner import limpiar_texto


def test_limpieza_basica():
    print("\n[1] Test de limpieza básica iniciado...")
    texto = "¡Hola! ¿Cómo estás? Esto es un test..."
    esperado = "hola cómo estás esto es un test"
    resultado = limpiar_texto(texto)
    assert resultado == esperado, f"[❌ ERROR] Resultado inesperado: {resultado}"
    print("✅ Test de limpieza básica superado.")


def test_eliminacion_urls():
    print("\n[2] Test de eliminación de URLs iniciado...")
    texto = "Visita http://example.com para más info"
    esperado = "visita para más info"
    resultado = limpiar_texto(texto)
    assert resultado == esperado, f"[❌ ERROR] Resultado inesperado: {resultado}"
    print("✅ Test de eliminación de URLs superado.")


def test_espacios_extra():
    print("\n[3] Test de eliminación de espacios múltiples iniciado...")
    texto = "Esto     es   un    texto   con   espacios"
    esperado = "esto es un texto con espacios"
    resultado = limpiar_texto(texto)
    assert resultado == esperado, f"[❌ ERROR] Resultado inesperado: {resultado}"
    print("✅ Test de eliminación de espacios múltiples superado.")


# Ejecutamos todos los tests si se corre el archivo directamente
if __name__ == "__main__":
    print("\n==============================================")
    print("🚀 Iniciando Tests de Limpieza de Texto (cleaner.py)")
    print("==============================================")

    test_limpieza_basica()
    test_eliminacion_urls()
    test_espacios_extra()

    print("\n🎯 Todos los tests de Cleaner finalizados correctamente.\n")
