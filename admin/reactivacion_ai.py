from telegram import Update
from telegram.ext import ContextTypes
from services.campanas import registrar_campana
from datetime import datetime

from user_service import load_users

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

<<<<<<< HEAD
ADMIN_ID = "7816979989"
=======
ADMIN_ID = 0
>>>>>>> 10fde51dda9db15dc5b5914f0b8e757c10d8951c


async def reactivar_inactivos(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = str(update.effective_user.id)

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ No autorizado"
        )

        return

    # GPT GENERA MENSAJE

    prompt = """
Crea un mensaje fitness motivacional
para usuarios que no entrenan hace días.

Máximo 40 palabras.
Con energía y CTA.
"""

    respuesta = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": "Eres experto en fitness marketing"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    mensaje = respuesta.choices[0].message.content

    usuarios = load_users()

    enviados = 0

    hoy = datetime.now()

    for uid, data in usuarios.items():

        ultima = data.get("ultima_actividad")

        if not ultima:
            continue

        try:

            fecha = datetime.strptime(
                ultima,
                "%Y-%m-%d %H:%M:%S.%f"
            )

            dias = (hoy - fecha).days

            if dias >= 7:

                await context.bot.send_message(
                    chat_id=uid,
                    text=mensaje
                )

                enviados += 1

        except Exception as e:

            print(e)
    registrar_campana(
    "reactivacion_inactivos",
    mensaje,
    enviados
)
    await update.message.reply_text(
        f"""
🤖 Campaña IA enviada

Mensaje:
{mensaje}

🔥 Usuarios reactivados: {enviados}
"""
    )