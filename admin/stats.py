from user_service import get_all_users

async def stats_command(update, context):

    users = get_all_users()

    total_clientes = len(users)

    text = (
        f"📊 BRIGHT PLACE SPOT STATS\n\n"
        f"👥 Clientes: {total_clientes}\n"
    )

    await update.message.reply_text(text)