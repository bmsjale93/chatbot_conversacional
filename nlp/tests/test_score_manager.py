from core.score_manager import (
    asignar_puntuacion,
    obtener_puntuaciones,
    eliminar_puntuaciones,
    generar_resumen_evaluacion
)
import uuid


def test_score_manager():
    print("\n🚀 Iniciando test de puntuación emocional...\n")

    session_id = str(uuid.uuid4())

    # Registrar puntuaciones
    asignar_puntuacion(session_id, "frecuencia", "Todos los días")
    asignar_puntuacion(session_id, "duracion", "Unas horas")
    asignar_puntuacion(session_id, "intensidad", "9")

    # Recuperar
    punt = obtener_puntuaciones(session_id)
    assert punt["frecuencia"] == 3
    assert punt["duracion"] == 1
    assert punt["intensidad"] == 3
    assert punt["total"] == 7
    print("✅ Puntuaciones correctamente almacenadas.")

    resumen = generar_resumen_evaluacion(session_id)
    assert resumen["evaluacion"] == "grave"
    print("✅ Resumen de evaluación generado:", resumen)

    eliminar_puntuaciones(session_id)
    assert obtener_puntuaciones(session_id) == {}
    print("✅ Puntuaciones eliminadas correctamente.")

    print("\n🎯 Test de score_manager completado.\n")


if __name__ == "__main__":
    test_score_manager()
