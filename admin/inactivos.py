from telegram import Update
from telegram.ext import ContextTypes

from datetime import datetime

from user_service import load_users

ADMIN_ID = "7816979989"


async def broadcast_inactivos(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = str(update.effective_user.id)

    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "❌ No autorizado"
        )
        return

    mensaje = " ".join(context.args)

    if not mensaje:
        await update.message.reply_text(
            "Uso:\n/broadcast_inactivos Hola 💪"
        )
        return

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

            print("UID:", uid)
            print("ULTIMA:", ultima)
            print("DIAS:", dias)

            if dias >= 7:

                await context.bot.send_message(
                    chat_id=uid,
                    text=mensaje
                )

                enviados += 1

        except Exception as e:

            print(e)

    await update.message.reply_text(
        f"🔥 Broadcast enviado a {enviados} inactivos"
    )