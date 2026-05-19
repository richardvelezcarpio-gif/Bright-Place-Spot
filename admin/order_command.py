from telegram.ext import ConversationHandler
ADMIN_ID = 0

PRODUCT, QUANTITY, NOTE = range(3)

ADMIN_ID = 559133702


async def start_order(update, context):

    await update.message.reply_text(
        "📦 ¿Qué producto deseas pedir?"
    )

    return PRODUCT


async def get_product(update, context):

    context.user_data["product"] = update.message.text

    await update.message.reply_text(
        "🔢 ¿Cantidad?"
    )

    return QUANTITY


async def get_quantity(update, context):

    context.user_data["quantity"] = update.message.text

    await update.message.reply_text(
        "📝 Escribe una nota o escribe 'no'"
    )

    return NOTE


async def finish_order(update, context):

    note = update.message.text

    user = update.effective_user

    product = context.user_data["product"]

    quantity = context.user_data["quantity"]

    mensaje = f"""
🔥 NUEVO PEDIDO

👤 Distribuidor: {user.first_name}

📦 Producto: {product}

🔢 Cantidad: {quantity}

📝 Nota: {note}
"""

    try:

        if ADMIN_ID != 0:

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=mensaje
            )

            print("✅ MENSAJE ENVIADO")

    except Exception as e:

        print(f"❌ ERROR TELEGRAM: {e}")

    await update.message.reply_text(
        "✅ Pedido enviado correctamente."
    )

    return ConversationHandler.END