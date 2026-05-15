def get_response(message):

    text = message.lower()

    if "hola" in text:
        return "Hola 😊 Bienvenido a nuestro club Herbalife."

    if "proteina" in text:
        return "Tenemos proteína Herbalife disponible 💪"

    if "horario" in text:
        return "Nuestro horario es de 7am a 2pm ☀️"

    return "Gracias por escribirnos 😊"


def detectar_objetivo(texto):

    texto = texto.lower()

    if "bajar grasa" in texto:
        return "bajar_grasa"

    if "subir masa" in texto:
        return "subir_masa"

    if "musculo" in texto:
        return "ganar_musculo"

    if "músculo" in texto:
        return "ganar_musculo"

    if "energia" in texto:
        return "energia"

    return None

def detectar_producto(texto):

    texto = texto.lower()

    productos = []

    if "proteina" in texto:
        productos.append("proteina")

    if "té" in texto:
        productos.append("te")

    if "te" in texto:
        productos.append("te")

    if "aloe" in texto:
        productos.append("aloe")

    return productos