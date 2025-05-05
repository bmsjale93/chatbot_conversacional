from pymongo import MongoClient
import os

def limpiar_base_de_datos():
    # Usa localhost directamente si estás en desarrollo local
    mongo_url = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    
    cliente = MongoClient(mongo_url)
    db = cliente.get_database("chatbot")

    colecciones = db.list_collection_names()

    if not colecciones:
        print("No hay colecciones para limpiar.")
        return

    for coleccion in colecciones:
        resultado = db[coleccion].delete_many({})
        print(f"🗑️  Colección '{coleccion}' limpiada. Documentos eliminados: {resultado.deleted_count}")

    print("✅ Base de datos limpiada con éxito.")

if __name__ == "__main__":
    limpiar_base_de_datos()
