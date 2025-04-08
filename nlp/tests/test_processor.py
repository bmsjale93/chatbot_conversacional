from core.processor import preprocesar_texto


def test_tokenizacion_basica():
    texto = "Me siento cansado y sin energía últimamente."
    resultado = preprocesar_texto(texto)

    print("\n🔹 Verificando tokenización y lematización básicas...")

    assert isinstance(
        resultado, list), "[❌ ERROR] El resultado no es una lista."

    assert "cansado" in resultado, "[❌ ERROR] Token 'cansado' no encontrado."
    assert "energía" in resultado, "[❌ ERROR] Token 'energía' no encontrado."
    assert "sentir" in resultado, "[❌ ERROR] Token 'sentir' (lematización de 'siento') no encontrado."

    print("✅ Tokenización y lematización correctas.")


def test_eliminacion_stopwords():
    texto = "Estoy muy pero muy feliz de estar aquí"
    resultado = preprocesar_texto(texto)

    print("\n🔹 Verificando eliminación de stopwords...")

    assert "feliz" in resultado, "[❌ ERROR] 'feliz' debería permanecer."
    assert "muy" not in resultado, "[❌ ERROR] 'muy' no debería aparecer."
    assert "pero" not in resultado, "[❌ ERROR] 'pero' no debería aparecer."

    print("✅ Eliminación de stopwords correcta.")


# Ejecutar todos los tests si el archivo se corre directamente
if __name__ == "__main__":
    print("\n==============================================")
    print("🚀 Iniciando Tests de Procesamiento de Texto (processor.py)")
    print("==============================================")

    test_tokenizacion_basica()
    test_eliminacion_stopwords()

    print("\n🎯 Todos los tests de Procesador de Texto pasaron correctamente.\n")
