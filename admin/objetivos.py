from telegram import Update
from telegram.ext import ContextTypes

from user_service import load_users


ADMIN_ID = 0


async def broadcast_objetivo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = str(update.effective_user.id)

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ No autorizado"
        )

        return

    if len(context.args) < 2:

        await update.message.reply_text(
            "Uso:\n/broadcast_objetivo objetivo mensaje"
        )

        return

    objetivo = context.args[0].lower()

    mensaje = " ".join(context.args[1:])

    usuarios = load_users()

    enviados = 0

    for uid, data in usuarios.items():

        objetivo_usuario = (
            data.get("objetivo", "")
            .lower()
            .strip()
        )

        if objetivo_usuario == objetivo:

            try:

                await context.bot.send_message(
                    chat_id=uid,
                    text=mensaje
                )

                enviados += 1

            except Exception as e:

                print(e)

    await update.message.reply_text(
        f"🎯 Broadcast enviado a {enviados} usuarios con objetivo: {objetivo}"
    )