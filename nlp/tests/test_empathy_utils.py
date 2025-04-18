import unittest
from core.empathy_utils import (
    detectar_ambiguedad,
    generar_respuesta_aclaratoria,
    generar_respuesta_empatica
)


class TestEmpathyUtils(unittest.TestCase):

    def test_detectar_ambiguedad_positiva(self):
        ejemplos = ["no sé", "Quizás", "npi", "No estoy seguro"]
        for texto in ejemplos:
            with self.subTest(texto=texto):
                self.assertTrue(detectar_ambiguedad(texto))

    def test_detectar_ambiguedad_negativa(self):
        ejemplos = ["Todos los días", "Una semana", "8", "Sí"]
        for texto in ejemplos:
            with self.subTest(texto=texto):
                self.assertFalse(detectar_ambiguedad(texto))

    def test_generar_respuesta_aclaratoria(self):
        estado = "preguntar_duracion"
        respuesta = generar_respuesta_aclaratoria(estado)
        self.assertEqual(respuesta["estado"], estado)
        self.assertIn("Permíteme explicarlo", respuesta["mensaje"])

    def test_generar_respuesta_empatica(self):
        base = "¿Con qué frecuencia te sientes triste?"
        salida = generar_respuesta_empatica(base, tipo="tristeza")
        self.assertTrue(salida.startswith("Lamento que te sientas así"))
        self.assertIn(base, salida)

        salida_neutro = generar_respuesta_empatica(base, tipo="neutro")
        self.assertEqual(salida_neutro, base)  # sin frase adicional


if __name__ == "__main__":
    unittest.main()
