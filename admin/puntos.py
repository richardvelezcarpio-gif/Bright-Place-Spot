from telegram import Update
from telegram.ext import ContextTypes

from user_service import (
    load_users,
    save_users
)

<<<<<<< HEAD
ADMIN_ID = "7816979989"
=======
ADMIN_ID = 0
>>>>>>> 10fde51dda9db15dc5b5914f0b8e757c10d8951c


async def dar_puntos(
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
            "Uso:\n/dar_puntos nombre puntos"
        )

        return

    nombre = context.args[0].lower()

    puntos = int(context.args[1])

    usuarios = load_users()

    encontrado = False

    for uid, data in usuarios.items():

        nombre_usuario = (
            data.get("nombre", "")
            .lower()
            .strip()
        )

        if nombre_usuario == nombre:

            actuales = data.get("puntos", 0)

            data["puntos"] = actuales + puntos

            encontrado = True

            save_users(usuarios)

            await update.message.reply_text(
                f"⭐ {puntos} puntos agregados a {nombre_usuario}"
            )

            break

    if not encontrado:

        await update.message.reply_text(
            "Usuario no encontrado"
        )