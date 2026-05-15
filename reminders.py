from datetime import time


async def recordatorio_diario(context):

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


def configurar_recordatorios(application, usuarios):

    application.bot_data["usuarios"] = usuarios

    job_queue = application.job_queue

    job_queue.run_daily(
        recordatorio_diario,
        time=time(hour=8, minute=0)
    )