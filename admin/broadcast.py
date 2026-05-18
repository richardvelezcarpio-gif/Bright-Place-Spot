from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from user_service import load_users

<<<<<<< HEAD
ADMIN_ID = "7816979989"
=======
ADMIN_ID = 0
>>>>>>> 10fde51dda9db15dc5b5914f0b8e757c10d8951c


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    # VALIDAR ADMIN
    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "❌ No autorizado"
        )
        return

    # OBTENER MENSAJE
    mensaje = " ".join(context.args)

    if not mensaje:
        await update.message.reply_text(
            "Uso:\n/broadcast Hola equipo 💪"
        )
        return

    usuarios = load_users()

    enviados = 0
    errores = 0

    # RECORRER USUARIOS
    for uid in usuarios.keys():

        try:

            await context.bot.send_message(
                chat_id=uid,
                text=mensaje
            )

            enviados += 1

        except Exception as e:

            print(f"Error con {uid}: {e}")

            errores += 1

    await update.message.reply_text(
        f"""
📢 Broadcast completado

✅ Enviados: {enviados}
❌ Errores: {errores}
"""
    )