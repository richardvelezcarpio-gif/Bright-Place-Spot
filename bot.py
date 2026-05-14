import json
import os
from datetime import datetime
from datetime import time

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# =========================
# TOKEN BOT
# =========================
TOKEN = "8917175568:AAEbqkKH1Arrtc3JB9dC3iAWGEVGS0IU4ig"

# =========================
# ESTADOS
# =========================
NOMBRE, META = range(2)

# =========================
# ARCHIVO JSON
# =========================
ARCHIVO_USUARIOS = "usuarios.json"


# =========================
# CARGAR USUARIOS
# =========================
def cargar_usuarios():

    if os.path.exists(ARCHIVO_USUARIOS):

        with open(ARCHIVO_USUARIOS, "r") as archivo:

            return json.load(archivo)

    return {}


# =========================
# GUARDAR USUARIOS
# =========================
def guardar_usuarios(data):

    with open(ARCHIVO_USUARIOS, "w") as archivo:

        json.dump(data, archivo, indent=4)


# =========================
# BASE DE DATOS
# =========================
usuarios = cargar_usuarios()


# =========================
# RECORDATORIO AUTOMÁTICO
# =========================
async def recordatorio(context: ContextTypes.DEFAULT_TYPE):

    usuarios = cargar_usuarios()

    for user_id in usuarios:

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text="""
🌱 RECUERDO DEL DÍA

Tu salud es una inversión diaria 💚

🥤 Tus batidos y té están disponibles hoy en FitClub Nutrition.
"""
            )

        except Exception as e:

            print(f"Error enviando mensaje a {user_id}: {e}")

  # CLIENTES INACTIVOS
async def revisar_inactivos(context: ContextTypes.DEFAULT_TYPE):

    usuarios = cargar_usuarios()

    hoy = datetime.now()

    for user_id, data in usuarios.items():

        ultima_visita = data.get("ultima_visita", "")

        if ultima_visita:

            fecha_visita = datetime.strptime(
                ultima_visita,
                "%Y-%m-%d"
            )

            dias = (hoy - fecha_visita).days

            if dias >= 3:

                try:

                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"""
💚 Hace {dias} días que no vienes a FitClub Nutrition.

Tu cuerpo merece seguir avanzando 🌱

🥤 Te esperamos hoy en el club.
"""
                    )

                except Exception as e:

                    print(e)          
# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🌱 Bienvenido a FitClub Nutrition\n\n¿Cómo te llamas?"
    )

    return NOMBRE


# =========================
# GUARDAR NOMBRE
# =========================
async def guardar_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):

    nombre = update.message.text

    context.user_data["nombre"] = nombre

    keyboard = [
        ["🔥 Bajar peso"],
        ["💪 Ganar músculo"],
        ["⚡ Más energía"],
        ["❤️ Bienestar"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        f"Mucho gusto {nombre} 💚\n\n¿Cuál es tu meta principal?",
        reply_markup=reply_markup
    )

    return META


# =========================
# GUARDAR META
# =========================
async def guardar_meta(update: Update, context: ContextTypes.DEFAULT_TYPE):

    meta = update.message.text
    nombre = context.user_data["nombre"]

    user_id = str(update.message.from_user.id)

    usuarios[user_id] = {
        "nombre": nombre,
        "meta": meta,
        "puntos": 0,
        "visitas": 0,
"ultima_visita": ""
    }

    guardar_usuarios(usuarios)

    keyboard = [
        ["🥤 Menú", "🎯 Mi progreso"],
        ["✅ Registrar visita", "🏆 Mis puntos"],
        ["💧 Recordatorios", "📍 Horarios"],
        ["🤝 Negocio Herbalife", "👤 Mi cuenta"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        f"""
✅ Registro completado

👤 Nombre: {nombre}
🎯 Meta: {meta}

Bienvenido a FitClub Nutrition 🌱
""",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


# =========================
# RESPONDER BOTONES
# =========================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text

    user_id = str(update.message.from_user.id)

    # =========================
    # MENÚ
    # =========================
    if texto == "🥤 Menú":

        await update.message.reply_text(
            """
🥤 MENÚ FITCLUB

• Batido Energético
• Batido Proteico
• Aloe Herbal
• Té Energizante
"""
        )

    # =========================
    # HORARIOS
    # =========================
    elif texto == "📍 Horarios":

        await update.message.reply_text(
            """
📍 HORARIOS

Lunes a Viernes:
7 AM - 7 PM

Sábados:
8 AM - 2 PM
"""
        )

    # =========================
    # RECORDATORIOS
    # =========================
    elif texto == "💧 Recordatorios":

        await update.message.reply_text(
            """
💧 Tus recordatorios diarios fueron activados 🌱
"""
        )

    # =========================
    # REGISTRAR VISITA
    # =========================
    elif texto == "✅ Registrar visita":

        if user_id in usuarios:

            usuarios[user_id]["visitas"] += 1
            usuarios[user_id]["ultima_visita"] = datetime.now().strftime("%Y-%m-%d")
            usuarios[user_id]["puntos"] += 10

            guardar_usuarios(usuarios)

            puntos = usuarios[user_id]["puntos"]
            visitas = usuarios[user_id]["visitas"]

            premio = ""

            if puntos >= 500:

                premio = "👑 Nivel VIP desbloqueado"

            elif puntos >= 200:

                premio = "🎁 Kit FitClub desbloqueado"

            elif puntos >= 100:

                premio = "🥤 Batido gratis desbloqueado"

            elif puntos >= 50:

                premio = "🧋 Té gratis desbloqueado"

            await update.message.reply_text(
                f"""
✅ VISITA REGISTRADA

🏆 Ganaste 10 puntos

⭐ Puntos actuales: {puntos}
🥤 Visitas totales: {visitas}

🎁 Recompensa actual:
{premio}

Gracias por cuidar tu salud 🌱
"""
            )

    # =========================
    # MIS PUNTOS
    # =========================
    elif texto == "🏆 Mis puntos":

        if user_id in usuarios:

            puntos = usuarios[user_id]["puntos"]
            visitas = usuarios[user_id]["visitas"]

            await update.message.reply_text(
                f"""
🏆 SISTEMA DE PUNTOS

⭐ Puntos acumulados: {puntos}

🥤 Visitas registradas: {visitas}

🎁 Premio disponible cada 100 puntos.

Sigue avanzando 💚
"""
            )

    # =========================
    # MI PROGRESO
    # =========================
    elif texto == "🎯 Mi progreso":

        await update.message.reply_text(
            """
🎯 Muy pronto podrás registrar:
• peso
• metas
• resultados
"""
        )

    # =========================
    # MI CUENTA
    # =========================
    elif texto == "👤 Mi cuenta":

        if user_id in usuarios:

            usuario = usuarios[user_id]

            await update.message.reply_text(
                f"""
👤 PERFIL

Nombre: {usuario['nombre']}
Meta: {usuario['meta']}
Estado: Activo 🌱
"""
            )

    # =========================
    # NEGOCIO HERBALIFE
    # =========================
    elif texto == "🤝 Negocio Herbalife":

        await update.message.reply_text(
            """
🔥 Construye ingresos ayudando personas a mejorar su salud 💚
"""
        )


# =========================
# CANCELAR
# =========================
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Proceso cancelado",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


# =========================
# APP
# =========================
app = ApplicationBuilder().token(TOKEN).build()


# =========================
# CONVERSACIÓN
# =========================
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],

    states={

        NOMBRE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                guardar_nombre
            )
        ],

        META: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                guardar_meta
            )
        ],
    },

    fallbacks=[CommandHandler("cancel", cancelar)]
)

# =========================
# HANDLERS
# =========================
app.add_handler(conv_handler)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        responder
    )
)

# =========================
# RECORDATORIO DIARIO
# =========================
job_queue = app.job_queue

job_queue.run_daily(
    recordatorio,
    time=time(hour=8, minute=0)
)

job_queue.run_daily(
    revisar_inactivos,
    time=time(hour=12, minute=0)
)

print("🚀 BOT ENCENDIDO...")

# =========================
# RUN
# =========================
app.run_polling()