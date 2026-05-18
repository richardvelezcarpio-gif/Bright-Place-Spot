from user_service import get_all_users

async def cliente_command(update, context):

    users = get_all_users()

    if not context.args:
        await update.message.reply_text(
            "Usa: /cliente nombre"
        )
        return

    nombre_busqueda = " ".join(context.args).lower()

    encontrado = None

    for user_id, user_data in users.items():

        nombre = str(user_data.get("nombre", "")).strip().lower()
        nombre_buscado = " ".join(context.args)
        if nombre_buscado.strip().lower() in nombre:
            encontrado = user_data
            break

    if not encontrado:
        await update.message.reply_text(
            "Cliente no encontrado."
        )
        return

    nombre = encontrado.get("nombre", "Sin nombre")
    objetivo = encontrado.get("objetivo", "No definido")
    puntos = encontrado.get("puntos", 0)
    visitas = encontrado.get("visitas", 0)
    mensajes = len(encontrado.get("historial", []))
    productos = encontrado.get("productos", [])

    productos_texto = "\n".join(
        [f"- {p}" for p in productos]
    )

    if not productos_texto:
        productos_texto = "Sin productos"

    texto = (
        f"👤 {nombre}\n\n"
        f"🎯 Objetivo: {objetivo}\n"
        f"⭐ Puntos: {puntos}\n"
        f"📅 Visitas: {visitas}\n"
        f"💬 Mensajes: {mensajes}\n\n"
        f"🥤 Productos:\n"
        f"{productos_texto}"
    )

    await update.message.reply_text(texto)