from core.emotion_model import analizar_sentimiento

# Asociación entre estados esperados y devueltos
TRADUCCION_ESTADOS = {
    "negativo": "negativo",
    "positivo": "positivo",
    "neutral": "neutro"
}


def test_analizar_sentimiento():
    textos = [
        ("Hoy me siento triste y sin ganas de nada.", "negativo"),
        ("¡Qué buen día! Estoy muy feliz.", "positivo"),
        ("No sé bien cómo me siento.", "neutral")
    ]

    resultados_ok = 0
    resultados_warn = 0

    print("\n==============================================")
    print("🚀 Iniciando Tests de Análisis Emocional (emotion_model.py)")
    print("==============================================\n")

    for idx, (texto, esperado) in enumerate(textos, 1):
        print(f"[{idx}] Analizando: '{texto[:40]}...'")
        resultado = analizar_sentimiento(texto)

        estado_detectado = resultado.get("estado_emocional", "").lower()

        # Extraemos la confianza correctamente
        confianza_str = resultado.get("confianza", "0%").replace("%", "")
        try:
            # Convertimos a float entre 0.0 y 1.0
            score = float(confianza_str) / 100
        except ValueError:
            score = 0.0

        esperado_convertido = TRADUCCION_ESTADOS.get(esperado, esperado)

        # Comprobamos el estado emocional
        try:
            assert estado_detectado == esperado_convertido, (
                f"[❌ ERROR] Para el texto '{texto[:30]}...', "
                f"esperábamos '{esperado_convertido}' pero se detectó '{estado_detectado}'"
            )
        except AssertionError as e:
            print(e)
            continue

        # Mostramos el estado detectado
        print(f"✅ Estado detectado: {estado_detectado} (Score: {score:.2f})")

        # Verificamos confianza
        if score < 0.7:
            print(
                f"⚠️ Score bajo ({score:.2f}) para '{texto[:30]}...' (posible baja confianza)")
            resultados_warn += 1
        else:
            resultados_ok += 1

    # Resumen final
    print("\n==============================================")
    print(f"✅ Tests correctos: {resultados_ok}")
    print(f"⚠️ Tests con baja confianza: {resultados_warn}")
    print("==============================================\n")


if __name__ == "__main__":
    test_analizar_sentimiento()
