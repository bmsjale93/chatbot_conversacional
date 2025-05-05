import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp.core.emotion_model import analizar_sentimiento, EMOCIONES_VALIDAS

# Silenciar advertencia de symlinks en Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def assert_in(item, container, message):
    assert item in container, f"❌ {message} — obtenido: '{item}'"

def assert_equal(a, b, message):
    assert a == b, f"❌ {message} — obtenido: '{a}' esperado: '{b}'"

def assert_keys(d, keys, message):
    for key in keys:
        assert key in d, f"❌ {message} — falta clave '{key}' en {d}"

print("🔍 Iniciando pruebas del análisis de sentimiento...\n")

try:
    # Prueba 1: tristeza
    resultado = analizar_sentimiento("Últimamente me siento muy triste y sin ganas de nada.")
    assert_equal(resultado["estado_emocional"], "tristeza", "Emoción incorrecta para tristeza")
    print("✅ Test: tristeza")

    # Prueba 2: alegría
    resultado = analizar_sentimiento("Hoy ha sido un día increíble, estoy muy feliz.")
    assert_equal(resultado["estado_emocional"], "alegría", "Emoción incorrecta para alegría")
    print("✅ Test: alegría")

    # Prueba 3: ansiedad
    resultado = analizar_sentimiento("Siento una presión constante en el pecho, no puedo relajarme.")
    assert_equal(resultado["estado_emocional"], "ansiedad", "Emoción incorrecta para ansiedad")
    print("✅ Test: ansiedad")

    # Prueba 4: frustración
    resultado = analizar_sentimiento("Estoy harto de que todo salga mal, me siento muy molesto.")
    assert_equal(resultado["estado_emocional"], "frustración", "Emoción incorrecta para enojo/frustración")
    print("✅ Test: frustración")

    # Prueba 5: esperanza
    resultado = analizar_sentimiento("Confío en que todo mejorará con el tiempo.")
    assert_equal(resultado["estado_emocional"], "esperanza", "Emoción incorrecta para esperanza")
    print("✅ Test: esperanza")

    # Prueba 6: sorpresa
    resultado = analizar_sentimiento("No me lo esperaba, fue una noticia completamente inesperada.")
    assert_equal(resultado["estado_emocional"], "sorpresa", "Emoción incorrecta para sorpresa")
    print("✅ Test: sorpresa")

    # Prueba 7: texto vacío
    resultado = analizar_sentimiento("   ")
    assert_equal(resultado["estado_emocional"], "desconocido", "Texto vacío debe retornar 'desconocido'")
    assert_equal(resultado["confianza"], "0%", "Texto vacío debe retornar 0% de confianza")
    print("✅ Test: texto vacío")

    # Prueba 8: ambigüedad
    resultado = analizar_sentimiento("No lo sé, a veces estoy bien, a veces no.")
    assert_in(resultado["estado_emocional"], EMOCIONES_VALIDAS + ["desconocido"], "Emoción ambigua no válida")
    print("✅ Test: ambigüedad")

    # Prueba 9: estructura del retorno
    resultado = analizar_sentimiento("Estoy bastante confundido últimamente.")
    assert_keys(resultado, ["estado_emocional", "confianza"], "Faltan claves en el resultado")
    print("✅ Test: estructura de retorno")

    print("\n🎉 Todas las pruebas pasaron correctamente.")

except AssertionError as e:
    print(str(e))
    print("❌ Al menos una prueba ha fallado.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
