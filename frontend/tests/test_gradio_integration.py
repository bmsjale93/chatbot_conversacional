# frontend/tests/test_gradio_integration.py

import requests
import time
import uuid


def test_gradio_integration():
    """
    Test de integración que comprueba que el frontend Gradio está levantado
    y se comunica correctamente con el backend.
    """
    session_id = str(uuid.uuid4())
    mensaje_usuario = "Hola, quiero comenzar"

    # Asegurarse de que el servidor Gradio esté levantado
    # Esto depende de cómo expongas la lógica en tu app
    url = "http://localhost:7860/chat"

    try:
        # Este endpoint depende de que hayas hecho accesible la API /chat también desde el frontend
        # Si no está expuesto, este test se puede adaptar para interactuar directamente con el backend
        response = requests.post(
            "http://backend:8000/chat",
            json={
                "session_id": session_id,
                "mensaje_usuario": mensaje_usuario
            },
            timeout=10
        )

        assert response.status_code == 200, f"Error: código de estado {response.status_code}"
        data = response.json()

        assert "mensaje" in data, "Falta la clave 'mensaje' en la respuesta"
        assert "estado" in data, "Falta la clave 'estado' en la respuesta"
        assert isinstance(data["mensaje"], str), "'mensaje' debe ser un string"
        assert isinstance(data["estado"], str), "'estado' debe ser un string"

        print("✅ Conexión completa Gradio ↔ Backend funcionando correctamente.")
        print(f"🧠 Respuesta: {data['mensaje']}")
        print(f"📌 Estado: {data['estado']}")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a Gradio. ¿Está el contenedor ejecutándose en el puerto 7860?")
        raise
    except Exception as e:
        print(f"❌ Error inesperado durante el test de integración: {e}")
        raise


if __name__ == "__main__":
    test_gradio_integration()
