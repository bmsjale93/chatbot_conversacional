import requests

# URL del endpoint de chat en el backend
url = "http://localhost:8000/chat"

# Datos que enviaremos al chatbot
data = {
    "mensaje_usuario": "Estoy muy cansado y sin energía"
}

# Cabeceras de la petición (formato JSON)
headers = {
    "Content-Type": "application/json"
}

# Intentamos enviar la petición al backend
try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()  # Lanza error si la respuesta no es 2xx

    # Si todo sale bien, mostramos la respuesta del chatbot
    print("✅ Respuesta del chatbot:")
    print(response.json())

except requests.exceptions.RequestException as e:
    # Si ocurre un error en la conexión o en la respuesta
    print("❌ Error al contactar con el backend:")
    print(e)
