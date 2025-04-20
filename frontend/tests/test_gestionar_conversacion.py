# tests/test_gestionar_conversacion.py

import requests
import uuid
import sys

def test_endpoint_gestionar_conversacion():
    print("🔍 Iniciando test de conversación completa vía /chat...", flush=True)

    # Endpoint del backend
    URL_BACKEND = "http://backend:8000/chat"

    # Generamos un session_id único para simular una sesión real
    session_id = str(uuid.uuid4())
    mensaje_usuario = "Hola, me siento un poco confundido hoy"

    payload = {
        "session_id": session_id,
        "mensaje_usuario": mensaje_usuario
    }

    try:
        response = requests.post(URL_BACKEND, json=payload, timeout=10)
        print(f"🔁 Código de estado HTTP: {response.status_code}", flush=True)
        assert response.status_code == 200, f"❌ Código inesperado: {response.status_code}"

        data = response.json()
        print("✅ Respuesta JSON recibida correctamente.", flush=True)

        # Comprobaciones clave
        assert isinstance(data, dict), "❌ La respuesta no es un diccionario"

        assert "mensaje" in data, "❌ Falta la clave 'mensaje' en la respuesta"
        assert isinstance(data["mensaje"], str), "❌ El campo 'mensaje' no es una cadena"

        assert "estado" in data, "❌ Falta la clave 'estado' en la respuesta"
        assert isinstance(data["estado"], str), "❌ El campo 'estado' no es una cadena"

        assert "sugerencias" in data, "❌ Falta la clave 'sugerencias' en la respuesta"
        assert isinstance(data["sugerencias"], list), "❌ El campo 'sugerencias' no es una lista"

        # Imprimir resultados detallados
        print(f"🧠 Mensaje recibido del asistente: {data['mensaje']}", flush=True)
        print(f"📌 Estado conversacional devuelto: {data['estado']}", flush=True)
        print(f"💡 Nº de sugerencias: {len(data['sugerencias'])}", flush=True)
        if data['sugerencias']:
            print(f"📋 Sugerencias: {data['sugerencias']}", flush=True)

        print("✅ Test de conversación gestionada correctamente.", flush=True)

    except Exception as e:
        print(f"❌ Error durante el test de gestión de conversación: {e}", flush=True)
        raise

# Si el script se ejecuta directamente
if __name__ == "__main__":
    test_endpoint_gestionar_conversacion()
