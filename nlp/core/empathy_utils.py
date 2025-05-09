from typing import Optional, Dict
from core.cleaner import limpiar_texto
from core.processor import preprocesar_texto
import re

# -------------------- Ambigüedad general --------------------

RESPUESTAS_AMBIGUAS = {
    "no sé", "no lo sé", "no lo se", "no estoy seguro", "no estoy segura", "quizás", "tal vez",
    "puede ser", "no entiendo", "no sé qué decir", "npi", "ni idea", "no sabría decir",
    "dudo", "estoy confundido", "no me queda claro", "no tengo claro", "no puedo responder",
    "creo que sí pero no sé", "no sé exactamente", "difícil de decir", "es complicado"
}

PALABRAS_CLAVE_AMBIGUAS = {
    "dudo", "confuso", "indeciso", "inseguro", "quizás", "tal", "vez",
    "complicado", "difícil", "ambigua", "ambigüedad", "confundido", "confundida"
}

PATRONES_AMBIGUOS = [
    re.compile(r"\bno\s+(lo\s+)?sé\b", re.IGNORECASE),
    re.compile(r"\bno\s+estoy\s+(seguro|segura)\b", re.IGNORECASE),
    re.compile(r"\bquizás\b", re.IGNORECASE),
    re.compile(r"\btal\s+vez\b", re.IGNORECASE),
    re.compile(r"\bpuede\s+ser\b", re.IGNORECASE),
    re.compile(r"\bni\s+idea\b", re.IGNORECASE),
    re.compile(r"\bno\s+entiendo\b", re.IGNORECASE),
    re.compile(r"\bno\s+sabría\s+decir\b", re.IGNORECASE),
    re.compile(r"\bno\s+(me\s+)?queda\s+claro\b", re.IGNORECASE),
    re.compile(r"\bes\s+complicado\b", re.IGNORECASE),
    re.compile(r"\bdifícil\s+de\s+decir\b", re.IGNORECASE),
    re.compile(r"\b(la verdad\s+)?(es que\s+)?no\s+(lo\s+)?sé\b", re.IGNORECASE)
]

def detectar_ambiguedad(texto: Optional[str]) -> bool:
    """
    Devuelve True si el texto se considera una respuesta ambigua.
    """
    if not texto:
        return True

    texto_original = texto.strip().lower()

    if texto_original in RESPUESTAS_AMBIGUAS:
        return True

    if any(p.search(texto_original) for p in PATRONES_AMBIGUOS):
        return True

    texto_limpio = limpiar_texto(texto_original)
    tokens = preprocesar_texto(texto_limpio)
    return any(token in PALABRAS_CLAVE_AMBIGUAS for token in tokens)

# -------------------- Mensajes de aclaración --------------------

def generar_respuesta_aclaratoria(estado_actual: str) -> Dict[str, str]:
    """
    Genera una respuesta para pedir aclaración al usuario manteniendo el mismo estado,
    adaptando el mensaje según el contexto del estado actual.
    """

    if estado_actual == "consentimiento":
        return {
            "estado": "consentimiento",
            "mensaje": (
                "No pasa nada si no estás seguro/a. Solo necesito saber si estás de acuerdo en continuar con esta evaluación.\n\n"
                "Tu información será tratada con confidencialidad y puedes dejarlo cuando quieras. "
                "¿Deseas seguir con la conversación?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Sí, estoy de acuerdo", "No, prefiero no continuar"]
        }

    if estado_actual == "preguntar_nombre":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no lo tienes claro. Puedes escribirme tu nombre real o un seudónimo con el que te sientas cómodo/a.\n\n"
                "Por ejemplo: 'Alejandro', 'Luna', 'Alex'."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": []
        }

    if estado_actual == "preguntar_identidad":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no sabes cómo describirte aún. Puedes escribirme cualquier etiqueta con la que te identifiques "
                "o simplemente cómo te gustaría que me refiera a ti.\n\n"
                "Por ejemplo: 'Masculino', 'Femenino', 'No binario', 'Agénero', 'Fluido', etc."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Masculino", "Femenino", "No binario"]
        }

    if estado_actual == "inicio_exploracion_tristeza":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no lo tienes del todo claro. A veces identificar cómo nos sentimos puede resultar confuso.\n\n"
                "Me gustaría saber si en los últimos días has experimentado algún momento de tristeza, malestar emocional o sensación de bajón. "
                "No importa si fue algo breve o si no estás seguro de cómo describirlo.\n\n"
                "¿Dirías que has pasado por algo así recientemente?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Sí, me he sentido triste", "No, me he sentido bien", "No estoy seguro"]
        }

    if estado_actual == "preguntar_frecuencia":
        return {
            "estado": estado_actual,
            "mensaje": (
                "No te preocupes si no puedes dar una respuesta exacta.\n\n"
                "Cuando te preguntaba por la frecuencia con la que sientes tristeza, me refería a si ocurre todos los días, algunas veces por semana, "
                "solo ocasionalmente o muy rara vez.\n\n"
                "¿Cómo describirías la frecuencia con la que sientes tristeza últimamente?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Todos los días", "A menudo", "De vez en cuando", "Rara vez"]
        }

    if estado_actual == "preguntar_duracion":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Gracias por compartirlo. Sé que a veces puede ser difícil precisar exactamente cuánto tiempo dura la tristeza.\n\n"
                "Solo necesito una idea general: ¿suele durar unos minutos, unas horas, varios días o incluso semanas?\n\n"
                "Puedes responder, por ejemplo: 'Unas horas', 'Dos días', 'Semanas', etc."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["Unas horas", "Dos días", "Semanas"]
        }

    if estado_actual == "intensidad_tristeza":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Entiendo que a veces puede ser complicado ponerle un número exacto a lo que sentimos.\n\n"
                "Solo necesito una idea general de cuán intensa es tu tristeza cuando aparece. "
                "Puedes indicarlo usando una escala del 1 (muy leve) al 10 (muy intensa), o algo aproximado como: "
                "'Creo que un 4' o 'más o menos un 7'."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["1", "5", "10"]
        }
    
    if estado_actual == "preguntar_empatia":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no tienes un número exacto ahora mismo.\n\n"
                "¿Podrías indicarme aproximadamente cómo te has sentido durante esta conversación conmigo?\n"
                "Utiliza una escala del 0 (nada empático) al 10 (muy empático), o una expresión como:\n"
                "'Más o menos un 6', 'Creo que un 7', 'Entre 4 y 5'."
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": ["3", "6", "10"]
        }
    
    if estado_actual == "preguntar_anhedonia":
        return {
            "estado": estado_actual,
            "mensaje": (
                "No pasa nada si no estás seguro/a. Me refiero a si últimamente has dejado de disfrutar cosas que antes te gustaban, "
                "como ver una película, estar con amigos, leer, hacer deporte o cualquier otra actividad que solías disfrutar.\n\n"
                "¿Dirías que has notado esa pérdida de interés o placer?"
            ),
            "modo_entrada": "texto_libre",
            "sugerencias": [
                "Sí, he perdido interés",
                "No, sigo disfrutando igual",
                "No lo sé"
            ]
        }
    
    if estado_actual == "detalle_anhedonia":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no sabes identificarlo con claridad aún.\n\n"
                "A veces dejamos de disfrutar ciertas cosas sin darnos cuenta. Me refiero a actividades como salir con amigos, escuchar música, hacer ejercicio, ver películas, etc.\n\n"
                "¿Hay alguna de esas cosas que sientas que ya no disfrutas como antes?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": ["Salir con amigos", "Escuchar música", "Hacer deporte"]
        }


    if estado_actual == "preguntar_desesperanza":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no lo tienes claro. A veces cuesta poner en palabras cómo nos sentimos con respecto al futuro.\n\n"
                "Cuando te pregunto si te cuesta encontrar algo que te motive o ilusione, me refiero a si ves difícil entusiasmarte con cosas por venir, ya sean planes, metas o actividades.\n\n"
                "¿Te sientes así últimamente?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": ["Sí, me cuesta ilusionarme", "No, tengo metas", "No estoy seguro"]
        }

    if estado_actual == "preguntar_inutilidad":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien si no sabes cómo expresarlo aún.\n\n"
                "A veces, cuando nos sentimos tristes o con la autoestima baja, podemos llegar a pensar que no somos suficientes o que no hacemos nada bien.\n\n"
                "¿Te ha pasado esto últimamente? Puedes responder, por ejemplo:\n"
                "'Sí, me he sentido así a veces' o 'No, en realidad no'."
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Sí, me ha pasado",
                "No, no me ha pasado",
                "No estoy seguro"
            ]
        }

    if estado_actual == "detalle_inutilidad":
        return {
            "estado": estado_actual,
            "mensaje": (
                "A veces cuesta identificar en qué momentos nos sentimos así.\n\n"
                "Cuando hablamos de sentir que no somos suficientes, pueden influir situaciones donde nos juzgamos, "
                "nos comparamos o sentimos que no cumplimos expectativas.\n\n"
                "¿En qué momentos se te suele pasar ese pensamiento por la cabeza?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": ["Cuando me equivoco", "Cuando me comparo", "Cuando estoy solo/a"]
        }


    if estado_actual == "preguntar_ideacion_suicida":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Entiendo que esta puede ser una pregunta difícil de responder. Lo importante es que puedas expresar lo que has sentido.\n\n"
                "Cuando hablo de ideación suicida, me refiero a pensamientos como:\n"
                "- 'Sería mejor no estar aquí'\n"
                "- 'La vida no tiene sentido'\n"
                "- 'He pensado en hacerme daño'\n\n"
                "¿Has tenido pensamientos como estos en los últimos días?"
            ),
            "modo_entrada": "sugerencias",
            "sugerencias": [
                "No entiendo la pregunta",
                "No, en ningún momento",
                "Sí, pero sin intención de hacerme daño",
                "Sí, pensé en hacerme daño, pero no tengo intención",
                "Sí, pensé en hacerme daño y tengo un plan"
            ]
        }

    if estado_actual == "preguntar_fatiga":
        return {
            "estado": estado_actual,
            "mensaje": (
                "A veces no es fácil notar cambios en nuestra energía hasta que nos detenemos a pensarlo.\n\n"
                "Me refiero a si últimamente te has sentido con menos energía de lo habitual, como si te costara más hacer las cosas, "
                "o te cansaras más rápido de lo normal, incluso con tareas cotidianas.\n\n"
                "¿Dirías que has notado algo así en los últimos días?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Sí, me siento más cansado/a",
                "No, tengo la misma energía de siempre",
                "No estoy seguro"
            ]
        }

    if estado_actual == "preguntar_sueno":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Con esta pregunta me refiero a si últimamente has notado cambios como:\n"
                "- Dormir más o menos de lo habitual\n"
                "- Dificultades para conciliar el sueño\n"
                "- Despertarte varias veces durante la noche\n\n"
                "¿Dirías que te está pasando algo de esto?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Sí, he notado cambios",
                "No, duermo bien",
                "No estoy seguro"
            ]
        }

    if estado_actual == "detalle_sueno":
        return {
            "estado": estado_actual,
            "mensaje": (
                "No te preocupes si no sabes cómo explicarlo con detalle aún.\n\n"
                "Puedes contarme si has notado cosas como:\n"
                "- Dormir menos de lo habitual\n"
                "- Despertarte con frecuencia\n"
                "- Tener dificultad para quedarte dormido/a\n"
                "- Dormir demasiado tiempo\n\n"
                "¿Cuál de estas dificultades te resulta más familiar?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Me cuesta dormirme",
                "Me despierto mucho",
                "Duermo menos horas",
                "Duermo más de lo habitual"
            ]
        }
    
    if estado_actual == "preguntar_apetito":
        return {
            "estado": estado_actual,
            "mensaje": (
                "No pasa nada si no estás seguro/a. Me refiero a si has notado algún cambio reciente en tu apetito, como:\n"
                "- Comer más de lo habitual\n"
                "- Tener menos hambre\n"
                "- Perder el interés por la comida\n\n"
                "¿Dirías que algo de esto te ha ocurrido últimamente?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Como más de lo habitual",
                "Como menos de lo habitual",
                "No he notado cambios",
                "No estoy seguro"
            ]
        }

    if estado_actual == "detalle_apetito":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Gracias por compartirlo. A veces cuesta describir con precisión los cambios en el apetito.\n\n"
                "Puedes contarme si has notado cosas como:\n"
                "- Comer mucho más o con más ansiedad\n"
                "- Perder el apetito por completo\n"
                "- Comer menos sin darte cuenta\n\n"
                "¿Cuál de estas situaciones te describe mejor últimamente?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Estoy comiendo más de lo normal",
                "Tengo menos apetito",
                "Como sin ganas",
                "He perdido el interés por la comida"
            ]
        }

    if estado_actual == "preguntar_concentracion":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Gracias por tu respuesta. Me refiero a si últimamente te ha costado mantener la atención en actividades como:\n"
                "- Leer un libro o artículo\n"
                "- Seguir una conversación\n"
                "- Hacer tareas del trabajo o los estudios\n\n"
                "¿Te ha ocurrido algo de esto recientemente?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Sí, me cuesta concentrarme",
                "No, me concentro bien",
                "No estoy seguro"
            ]
        }

    if estado_actual == "detalle_concentracion":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Está bien, a veces es difícil identificar exactamente en qué momentos falla la concentración.\n\n"
                "Puedes contarme si te pasa por ejemplo:\n"
                "- Al leer o estudiar\n"
                "- Cuando estás hablando con alguien\n"
                "- Mientras haces tareas que antes hacías con facilidad\n\n"
                "¿En qué situaciones lo notas más?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Leyendo",
                "Hablando con otras personas",
                "Trabajando o estudiando",
                "Haciendo tareas diarias"
            ]
        }

    if estado_actual == "preguntar_agitacion":
        return {
            "estado": estado_actual,
            "mensaje": (
                "No pasa nada si no estás seguro/a. Me refiero a si últimamente has sentido inquietud o agitación física o mental, como:\n"
                "- Necesidad de moverte constantemente\n"
                "- Sensación de estar acelerado o intranquilo\n"
                "- Dificultad para estar en calma\n\n"
                "¿Te ha ocurrido algo así?"
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Sí, me siento inquieto",
                "No, estoy tranquilo",
                "No estoy seguro"
            ]
        }

    if estado_actual == "detalle_agitacion":
        return {
            "estado": estado_actual,
            "mensaje": (
                "Gracias por comentarlo. La inquietud puede expresarse de muchas formas, como:\n"
                "- Moverte de un lado a otro\n"
                "- Sentir ansiedad en el cuerpo\n"
                "- Tener una sensación de urgencia constante\n\n"
                "Cuéntame cómo lo estás viviendo tú."
            ),
            "modo_entrada": "mixto",
            "sugerencias": [
                "Tengo sensación de urgencia constante",
                "Me muevo sin parar",
                "Me siento tenso e inquieto",
                "No puedo parar quieto"
            ]
        }

    return {
        "estado": estado_actual,
        "mensaje": (
            "Permíteme explicarlo de otra forma. No te preocupes si no tienes una respuesta clara aún, "
            "puedes tomarte tu tiempo para pensarla o decir lo primero que te venga a la mente."
        ),
        "modo_entrada": "texto_libre",
        "sugerencias": []
    }



# -------------------- Mensajes empáticos --------------------

def generar_respuesta_empatica(mensaje_base: str, tipo: str = "neutral") -> str:
    """
    Agrega una frase empática al inicio del mensaje base según la emoción detectada.
    """

    frases_empaticas = {
        "tristeza": (
            "Gracias por compartir cómo te sientes. La tristeza es una emoción válida, y no tienes que atravesarla solo/a. "
            "Estoy aquí contigo, para escucharte y acompañarte sin juicio. "
        ),
        "anhedonia": (
            "Perder el interés por cosas que antes disfrutabas puede sentirse desconcertante. No estás solo/a en esto, y hablarlo es un paso importante para entenderte mejor. "
        ),
        "alegría": (
            "Qué bonito que lo sientas así. Reconocer las emociones positivas también forma parte del cuidado emocional. "
            "Me alegra poder compartir este momento contigo. "
        ),
        "desesperanza": (
            "Sentir que no hay nada que motive o ilusione puede ser muy difícil. Agradezco que lo compartas. "
            "Reconocer esta sensación es un paso importante para buscar claridad y apoyo. "
        ),
        "inutilidad": (
            "A veces podemos ser muy críticos con nosotros mismos, sobre todo en momentos de vulnerabilidad emocional. "
            "Gracias por compartir esta parte tan personal. Hablar de ello puede ser un paso hacia una mirada más amable hacia ti mismo/a. "
        )
    }



    frase_intro = frases_empaticas.get(tipo, "Gracias por compartir cómo te sientes. ")
    return f"{frase_intro}{mensaje_base}"

# -------------------- Ambigüedad específica de identidad --------------------

RESPUESTAS_AMBIGUAS_IDENTIDAD = {
    "no lo sé", "no sé", "no estoy seguro", "no quiero decirlo",
    "prefiero no decirlo", "ninguno", "ninguna", "n/a", "no binarie",
    "sin definir", "no definido", "indefinido", "sin género", "sin genero",
    "sin identidad", "no quiero responder", "no sé qué soy"
}

def detectar_ambiguedad_identidad(texto: Optional[str]) -> bool:
    """
    Devuelve True si la respuesta sobre identidad se considera ambigua.
    """
    if not texto:
        return True
    texto_limpio = limpiar_texto(texto)
    return any(ambigua in texto_limpio for ambigua in RESPUESTAS_AMBIGUAS_IDENTIDAD)
