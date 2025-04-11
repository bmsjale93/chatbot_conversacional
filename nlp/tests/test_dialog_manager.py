from core import dialog_manager


def test_obtener_mensaje_presentacion():
    mensaje = dialog_manager.obtener_mensaje_presentacion()

    assert isinstance(mensaje, dict), "La respuesta debe ser un diccionario."
    assert "estado" in mensaje and "mensaje" in mensaje, "Faltan campos obligatorios."
    assert mensaje["estado"] == "presentacion", "El estado inicial debería ser 'presentacion'."
    print("✅ Test de presentación pasado.")


def test_formato_general_dialogos():
    funciones = [
        dialog_manager.obtener_mensaje_presentacion,
        dialog_manager.obtener_mensaje_nombre,
        dialog_manager.obtener_mensaje_identidad,
        dialog_manager.obtener_mensaje_exploracion_tristeza,
        dialog_manager.obtener_mensaje_frecuencia_tristeza,
        dialog_manager.obtener_mensaje_duracion_tristeza,
        dialog_manager.obtener_mensaje_intensidad_tristeza
    ]

    for func in funciones:
        resultado = func() if 'nombre_usuario' not in func.__code__.co_varnames else func("Usuario")
        assert isinstance(
            resultado, dict), f"❌ {func.__name__}: La salida no es un dict."
        assert "estado" in resultado and "mensaje" in resultado, f"❌ {func.__name__}: Faltan campos esenciales."
        assert isinstance(
            resultado["mensaje"], str), f"❌ {func.__name__}: El mensaje debe ser string."
        print(f"✅ {func.__name__} pasó correctamente.")


if __name__ == "__main__":
    print("\n🚀 Iniciando tests de Dialog Manager...\n")
    test_obtener_mensaje_presentacion()
    test_formato_general_dialogos()
    print("\n🎯 Todos los tests de Dialog Manager ejecutados correctamente.\n")
