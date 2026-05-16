import json
import os
from datetime import datetime, time

import openai

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

# IMPORTS LOCALES
from openai_service import generar_respuesta

from responses import (
    get_response,
    detectar_objetivo,
    detectar_producto
)

from user_service import (
    load_users,
    save_users,
    get_user_profile
)
from reminders import configurar_recordatorios
# =====================================
# TOKENS
# =====================================

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# =====================================
# ESTADOS
# =====================================

NOMBRE, META = range(2)

# =====================================
# ARCHIVO
# =====================================

ARCHIVO_USUARIOS = "usuarios.json"

# =====================================
# CARGAR USUARIOS
# =====================================

def cargar_usuarios():

    if os.path.exists(ARCHIVO_USUARIOS):

        with open(ARCHIVO_USUARIOS, "r") as archivo:

            return json.load(archivo)

    return {}

# =====================================
# GUARDAR USUARIOS
# =====================================

def guardar_usuarios(data):

    with open(ARCHIVO_USUARIOS, "w") as archivo:

        json.dump(data, archivo, indent=4)

# =====================================
# BASE DATOS
# =====================================

usuarios = cargar_usuarios()

# =========================================
# IA FITCLUB HÍBRIDA
# =========================================

async def responder_ia(user_id, mensaje_usuario):

    usuarios = cargar_usuarios()

    user_id = str(user_id)

    nombre = usuarios.get(user_id, {}).get("nombre", "")
    meta = usuarios.get(user_id, {}).get("meta", "")
    historial = usuarios.get(user_id, {}).get("historial", [])

    historial.append({
        "role": "user",
        "content": mensaje_usuario
    })

    historial = historial[-6:]

    mensajes = [

        {
            "role": "system",
            "content": f"""

Eres un coach  bright Place Spot.

El cliente se llama: {nombre}

Su meta principal es:
{meta}

Ayudas personas a:
- bajar peso
- ganar músculo
- ganar energía
- mejorar bienestar
- mejorar nutrición

Tu enfoque está basado en:
- nutrición saludable
- batidos
- motivación
- ejercicio
- bienestar
- productos Herbalife

Recomiendas productos Herbalife según la meta del cliente.

Hablas:
- positivo
- energético
- amigable
- motivador
- profesional

Nunca das diagnósticos médicos.
Nunca reemplazas médicos.
Nunca recomiendas medicamentos.
"""
        },

        {
            "role": "user",
            "content": mensaje_usuario
        }

    ]

    respuesta = generar_respuesta(
    mensajes,
    historial,
    usuarios,
    user_id,
    save_users
)
    nombre = usuarios.get(user_id, {}).get("nombre", "")

    respuesta_final = f"""
💚 {nombre}

{respuesta}

— Coach Alexandra
"""

    return respuesta_final
    
    
# =====================================
# RECORDATORIO AUTOMÁTICO
# =====================================

async def recordatorio(context: ContextTypes.DEFAULT_TYPE):

    usuarios = cargar_usuarios()

    for user_id in usuarios:

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text="""
🌱 RECORDATORIO DEL DÍA

Tu salud es una inversión diaria 💚

🥤 Tus batidos y té están disponibles hoy en FitClub Nutrition.
"""
            )

        except Exception as e:

            print(f"Error enviando mensaje a {user_id}: {e}")

# =====================================
# CLIENTES INACTIVOS
# =====================================

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
💚 Hace {dias} días que no vienes a Bright Place Spot.

Tu cuerpo merece seguir avanzando 🌱

🥤 Te esperamos hoy en el club.
"""
                    )

                except Exception as e:

                    print(e)

# =====================================
# START
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🌱 Bienvenido a Bright Place Spot\n\n¿Cómo te llamas?"
    )

    return NOMBRE

# =====================================
# GUARDAR NOMBRE
# =====================================

async def guardar_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):

    nombre = update.message.text

    context.user_data["nombre"] = nombre

    keyboard = [
        ["🔥 Bajar peso"],
        ["💪 Ganar músculo"],
        ["⚡ Más energía"],
        ["💚 Bienestar"]
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

# =====================================
# GUARDAR META
# =====================================

async def guardar_meta(update: Update, context: ContextTypes.DEFAULT_TYPE):

    meta = update.message.text

    nombre = context.user_data["nombre"]

    user_id = str(update.message.from_user.id)

    perfil = get_user_profile(usuarios, user_id)

    objetivo = detectar_objetivo(meta)

    if objetivo:

        perfil["objetivo"] = objetivo

    productos = detectar_producto(meta)

    for producto in productos:

        if producto not in perfil["productos"]:

            perfil["productos"].append(producto)

    usuarios[user_id] = {
        "nombre": nombre,
        "meta": meta,
        "puntos": 0,
        "visitas": 0,
        "ultima_visita": "",
        "historial": [],
        "objetivo": perfil.get("objetivo", ""),
        "productos": perfil.get("productos", [])
    }

    save_users(usuarios)

    keyboard = [
    ["🥤 Menú", "📈 Mi progreso"],
    ["✅ Registrar visita", "🏆 Mis puntos"],
    ["⏰ Recordatorios", "🕒 Horarios"],
    ["🤝 Negocio Herbalife", "👤 Mi cuenta"],
    ["📍 Dirección Club", "📞 Contacto Coach"]
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

Bienvenido a BrightPlace Spot
Cuentame cual es tu objetivo 🚀
""",
        reply_markup=reply_markup
    )

    return ConversationHandler.END

# =====================================
# RESPONDER BOTONES
# =====================================


# =========================================
# RESPONDER BOTONES + IA
# =========================================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text

    user_id = str(update.message.from_user.id)

    # =========================================
    # RESPUESTAS RÁPIDAS
    # =========================================

    respuesta_rapida = get_response(texto)

    if respuesta_rapida != "Gracias por escribirnos 😊":

        await update.message.reply_text(respuesta_rapida)
        return

    # =========================================
    # MENÚ
    # =========================================

    if texto == "🥤 Menú":

        await update.message.reply_text(
            """
🥤 MENÚ BRIGHT PLACE SPOT

• Batido Energético
• Batido Proteico
• Aloe Herbal
• Té Energizante
"""
        )
        return

    # =========================================
    # HORARIOS
    # =========================================

    elif texto == "🕒 Horarios":

        await update.message.reply_text(
            """
🕒 HORARIOS

Lunes a Viernes
7am - 2pm ☀️
"""
        )
        return
    
    # HORARIOS

        # =========================================
    # DIRECCIÓN CLUB
    # =========================================

    elif texto == "📍 Dirección Club":

        await update.message.reply_text(
            """
📍 BRIGHT PLACE SPOT

Tomillos L6 Y Las Retamas
Cuenca - Ecuador

✨ Te esperamos con la mejor energía.
"""
        )

        return

    # =========================================
    # CONTACTO COACH
    # =========================================

    elif texto == "📞 Contacto Coach":

        await update.message.reply_text(
    """
📞 COACH ALEXANDRA

💬 WhatsApp:
https://wa.me/593983830383

📸 Instagram:
https://www.instagram.com/brightplacespot/

💚 Estoy aquí para ayudarte.
"""
)

        return

    

        # =========================================
    # REGISTRAR VISITA
    # =========================================

    elif texto == "✅ Registrar visita":

        if user_id in usuarios:

            hoy = datetime.now().strftime("%Y-%m-%d")

            ultima_visita = usuarios[user_id].get("ultima_visita", "")

            # EVITAR DOBLE VISITA EL MISMO DÍA
            if ultima_visita == hoy:

                await update.message.reply_text(
                    """
⚠️ Ya registraste tu visita hoy.

💚 Te esperamos mañana nuevamente.
"""
                )

                return

            # REGISTRAR VISITA
            usuarios[user_id]["visitas"] += 1
            usuarios[user_id]["puntos"] += 10
            usuarios[user_id]["ultima_visita"] = hoy

            save_users(usuarios)

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

                premio = "🍵 Té gratis desbloqueado"

            await update.message.reply_text(
                f"""
✅ VISITA REGISTRADA

🏆 Ganaste 10 puntos

⭐ Puntos actuales: {puntos}
📍 Visitas totales: {visitas}

🎁 Recompensa actual:

{premio}

💚 Gracias por cuidar tu salud.
"""
            )

        return

    # =========================================
    # MIS PUNTOS
    # =========================================

    elif texto == "🏆 Mis puntos":

        if user_id in usuarios:

            puntos = usuarios[user_id]["puntos"]

            await update.message.reply_text(
                f"""
🏆 MIS PUNTOS

⭐ Tienes actualmente:
{puntos} puntos
"""
            )

        return

    # =========================================
    # MI CUENTA
    # =========================================

    elif texto == "👤 Mi cuenta":

        if user_id in usuarios:

            usuario = usuarios[user_id]

            await update.message.reply_text(
                f"""
👤 MI CUENTA

Nombre: {usuario.get("nombre", "")}

Meta: {usuario.get("meta", "")}

⭐ Puntos: {usuario.get("puntos", 0)}

✅ Visitas: {usuario.get("visitas", 0)}
"""
            )

        return

    # =========================================
    # IA
    # =========================================

    respuesta_ia = await responder_ia(user_id, texto)

    await update.message.reply_text(respuesta_ia)

# =====================================
# CANCELAR
# =====================================

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Proceso cancelado.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# =====================================
# APP
# =====================================

app = ApplicationBuilder().token(TOKEN).build()
configurar_recordatorios(app, usuarios)

# =====================================
# CONVERSACIÓN
# =====================================

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

# =====================================
# HANDLERS
# =====================================

app.add_handler(conv_handler)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        responder
    )
)

# =====================================
# RECORDATORIOS
# =====================================

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

# =====================================
# RUN
# =====================================

app.run_polling()