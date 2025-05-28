def destacar_pregunta_binaria(texto: str) -> str:
    """
    Prepara un texto marcándolo como pregunta afirmativa/negativa. 
    Renderizamos la cabecera en negrita cuando llegue al frontend.
    """
    cabecera = "**Indica SI o NO en tu Respuesta**\n"
    subencabezado = "*Por ejemplo, 'Si, continuemos.'*\n\n"
    return cabecera + subencabezado + texto