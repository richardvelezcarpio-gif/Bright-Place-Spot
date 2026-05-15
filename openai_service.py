from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generar_respuesta(
    mensajes,
    historial,
    usuarios,
    user_id,
    save_users
):

    respuesta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes + historial
    )

    respuesta_texto = respuesta.choices[0].message.content

    historial.append({
        "role": "assistant",
        "content": respuesta_texto
    })

    # CREAR USUARIO SI NO EXISTE
    if str(user_id) not in usuarios:

        usuarios[str(user_id)] = {
            "nombre": "",
            "meta": "",
            "puntos": 0,
            "visitas": 0,
            "ultima_visita": "",
            "historial": [],
            "objetivo": "",
            "productos": []
        }

    # GUARDAR HISTORIAL
    usuarios[str(user_id)]["historial"] = historial

    # GUARDAR CAMBIOS
    save_users(usuarios)

    return respuesta_texto