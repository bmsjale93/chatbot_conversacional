from core.conversation_state import (
    obtener_estado_usuario,
    guardar_estado_usuario,
    actualizar_estado_usuario,
    borrar_estado_usuario
)
import uuid
import time

def test_conversation_state():
    print("\n🚀 Iniciando test de Conversation State (gestión de estado de usuario)...\n")

    # Generamos un session_id único para no afectar otros datos
    session_id = str(uuid.uuid4())

    # Estado inicial que queremos guardar
    estado_inicial = {
        "estado_actual": "presentacion",
        "nombre_usuario": None
    }

    print(f"📝 Guardando estado inicial para sesión: {session_id}")
    guardar_estado_usuario(session_id, estado_inicial)

    time.sleep(1)

    # Recuperar estado y comprobar que se ha guardado
    estado_recuperado = obtener_estado_usuario(session_id)
    assert estado_recuperado is not None, "❌ No se pudo recuperar el estado."
    assert estado_recuperado["estado_actual"] == "presentacion", "❌ Estado actual incorrecto tras guardar."
    print("✅ Estado guardado y recuperado correctamente.")

    # Actualizar solo el estado actual
    nuevo_estado = "preguntar_nombre"
    actualizar_estado_usuario(session_id, nuevo_estado)

    time.sleep(1)

    estado_actualizado = obtener_estado_usuario(session_id)
    assert estado_actualizado["estado_actual"] == nuevo_estado, "❌ No se actualizó correctamente el estado actual."
    print("✅ Estado actualizado correctamente.")

    # Borrar estado
    borrar_estado_usuario(session_id)

    time.sleep(1)

    estado_borrado = obtener_estado_usuario(session_id)
    assert estado_borrado is None, "❌ El estado debería haber sido eliminado."
    print("✅ Estado eliminado correctamente.")

    print("\n🎯 Test de Conversation State completado exitosamente.\n")


# Ejecutar si se llama directamente
if __name__ == "__main__":
    test_conversation_state()