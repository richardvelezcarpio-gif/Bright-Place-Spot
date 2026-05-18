from user_service import get_all_users

async def clientes_command(update, context):

    users = get_all_users()

    if not users:
        await update.message.reply_text(
            "No hay clientes registrados."
        )
        return

    text = "👥 CLIENTES BRIGTH PACE SPOT\n\n"

    for i, (user_id, user_data) in enumerate(users.items(), start=1):

        nombre = user_data.get("nombre", "Sin nombre")

        text += f"{i}. {nombre}\n"

    text += f"\nTotal clientes: {len(users)}"

    await update.message.reply_text(text)