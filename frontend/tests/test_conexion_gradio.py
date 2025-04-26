import requests
import uuid

def test_conexion_backend():
    """
    Verifica que el frontend puede comunicarse correctamente con el backend FastAPI.
    """
    BACKEND_URL = "http://backend:8000/api/chat"
    session_id = str(uuid.uuid4())
    mensaje_usuario = "Hola, quiero comenzar la evaluación"

    try:
        response = requests.post(
            BACKEND_URL,
            json={
                "session_id": session_id,
                "mensaje_usuario": mensaje_usuario
            },
            timeout=10
        )

        assert response.status_code == 200, f"Error: código de estado {response.status_code}"
        data = response.json()

        assert "mensaje" in data, "La clave 'mensaje' no está presente en la respuesta"
        assert "estado" in data, "La clave 'estado' no está presente en la respuesta"
        assert isinstance(data["mensaje"], str), "'mensaje' debe ser un string"
        assert isinstance(data["estado"], str), "'estado' debe ser un string"

        print("✅ Test de conexión con backend superado.")
        print(f"🧠 Mensaje recibido: {data['mensaje']}")
        print(f"📌 Estado recibido: {data['estado']}")

    except Exception as e:
        print("❌ Error durante el test de conexión:", e)
        raise


# Ejecutar directamente si se corre el script
if __name__ == "__main__":
    test_conexion_backend()
