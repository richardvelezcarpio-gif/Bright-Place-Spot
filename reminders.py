from datetime import time
from user_service import load_users


async def recordatorio_diario(context):

    print("🔥 RECORDATORIO EJECUTÁNDOSE")

    usuarios = context.bot_data["usuarios"]

    for user_id, data in usuarios.items():

        nombre = data.get("nombre", "amigo")

        objetivo = data.get("objetivo", "")

        # MENSAJES PERSONALIZADOS

        if objetivo == "ganar_musculo":

            mensaje = f"""
💪 Hola {nombre}

Hoy es un gran día para construir músculo 🚀

No olvides:
• proteína
• hidratación
• entrenamiento

Te esperamos en FitClub 🔥
"""

        elif objetivo == "bajar_grasa":

            mensaje = f"""
🔥 Hola {nombre}

Hoy enfócate en:
• hidratación
• cardio
• nutrición limpia

Vamos con todo 🚀
"""

        else:

            mensaje = f"""
☀️ Hola {nombre}

No olvides tu nutrición hoy 💪

Te esperamos en FitClub 🚀
"""

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text=mensaje
            )

        except Exception as e:

            print(f"Error enviando a {user_id}: {e}")


async def configurar_recordatorios(update, context):

    usuarios = load_users()

    context.bot_data["usuarios"] = usuarios

    job_queue = context.job_queue

    # 7 AM
    job_queue.run_daily(
        recordatorio_diario,
        time=time(hour=7, minute=0)
    )

    # 7 PM
    job_queue.run_daily(
        recordatorio_diario,
        time=time(hour=19, minute=0)
    )

    await update.message.reply_text(
        "✅ Recordatorios activados 7AM y 7PM"
    )