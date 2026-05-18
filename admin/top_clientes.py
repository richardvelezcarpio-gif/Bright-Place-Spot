from telegram import Update
from telegram.ext import ContextTypes

from user_service import load_users

<<<<<<< HEAD
ADMIN_ID = "7816979989"
=======
ADMIN_ID = 0
>>>>>>> 10fde51dda9db15dc5b5914f0b8e757c10d8951c


async def top_clientes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = str(update.effective_user.id)

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ No autorizado"
        )

        return

    usuarios = load_users()

    ranking = []

    for uid, data in usuarios.items():

        nombre = data.get("nombre", "Cliente")

        visitas = data.get("visitas", 0)

        puntos = data.get("puntos", 0)

        score = visitas + puntos

        ranking.append({
            "nombre": nombre,
            "score": score,
            "visitas": visitas,
            "puntos": puntos
        })

    ranking.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    mensaje = "🏆 TOP CLIENTES FITCLUB\n\n"

    for i, cliente in enumerate(ranking[:10], start=1):

        mensaje += (
            f"{i}. {cliente['nombre']}\n"
            f"🔥 Score: {cliente['score']}\n"
            f"🏋️ Visitas: {cliente['visitas']}\n"
            f"⭐ Puntos: {cliente['puntos']}\n\n"
        )

    await update.message.reply_text(mensaje)