import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def generar_respuesta(
    mensajes,
    usuarios,
    user_id,
    save_users
):

    try:

        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=mensajes
        )

        respuesta_texto = respuesta["choices"][0]["message"]["content"]

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
        usuarios[str(user_id)]["historial"] = mensajes

        # GUARDAR CAMBIOS
        save_users(usuarios)

        return respuesta_texto

    except Exception as e:

        print(f"ERROR OPENAI: {e}")

        return "🤖 La IA está temporalmente fuera de servicio."