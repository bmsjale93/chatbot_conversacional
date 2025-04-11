from core.intent_detector import detectar_intencion


def test_respuesta_afirmativa():
    texto = "Claro que sí, quiero continuar"
    intencion = detectar_intencion(texto)
    assert intencion == "afirmativo", "❌ No detectó correctamente una intención afirmativa."
    print("✅ Test de respuesta afirmativa correcto.")


def test_respuesta_negativa():
    texto = "No deseo seguir con la evaluación"
    intencion = detectar_intencion(texto)
    assert intencion == "negativo", "❌ No detectó correctamente una intención negativa."
    print("✅ Test de respuesta negativa correcto.")


def test_respuesta_desconocida():
    texto = "Quizá más tarde"
    intencion = detectar_intencion(texto)
    assert intencion == "desconocido", "❌ Debería detectarlo como desconocido."
    print("✅ Test de respuesta desconocida correcto.")


if __name__ == "__main__":
    print("\n🚀 Iniciando tests de Intent Detector...\n")
    test_respuesta_afirmativa()
    test_respuesta_negativa()
    test_respuesta_desconocida()
    print("\n🎯 Todos los tests de Intent Detector ejecutados correctamente.\n")
