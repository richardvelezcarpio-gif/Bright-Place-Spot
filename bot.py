from dotenv import load_dotenv

load_dotenv()

import os
import json
from datetime import datetime, time
from admin.clientes import clientes_command
import openai
from admin.stats import stats_command
from admin.cliente import cliente_command
from user_service import save_users
from admin.broadcast import broadcast
from admin.inactivos import broadcast_inactivos
from admin.objetivos import broadcast_objetivo
from admin.campanas_ai import crear_campana_inactivos
from admin.reactivacion_ai import reactivar_inactivos
from admin.top_clientes import top_clientes
from services.campanas import ver_campanas
from admin.puntos import dar_puntos
from datetime import datetime
from telegram import Update
from telegram.ext import *
from admin.order_command import *

from user_service import (
    load_users,
    save_users
)
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


# ====================================
# CONFIGURACIÓN ADMIN
# ====================================

ADMIN_ID = 0
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
from datetime import datetime

async def responder_ia(update, user_id, mensaje_usuario):

    usuarios = cargar_usuarios()

    user_id = str(user_id)

    # ==============================
    # CREAR USUARIO SI NO EXISTE
    # ==============================

    if user_id not in usuarios:

        usuarios[str(user_id)] = {
            "nombre": update.effective_user.first_name,
            "meta": "",
            "historial": [],
            "visitas": 0,
            "ultima_actividad": "",
            "productos": [],
            "puntos": 0
        }

    # ==============================
    # ACTUALIZAR CRM
    # ==============================

    # ACTUALIZAR CRM

    usuarios[user_id]["nombre"] = update.effective_user.first_name

    usuarios[user_id]["visitas"] += 1

    usuarios[user_id]["ultima_actividad"] = str(datetime.now())

    # ==============================
    # OBTENER DATOS
    # ==============================

    nombre = usuarios[user_id].get("nombre", "amig@")

    meta = usuarios[user_id].get("meta", "")

    historial = usuarios[user_id].get("historial", [])

    # ==============================
    # GUARDAR MENSAJE USUARIO
    # ==============================

    historial.append({
        "role": "user",
        "content": mensaje_usuario
    })

    historial = historial[-6:]

    usuarios[user_id]["historial"] = historial

    guardar_usuarios(usuarios)

    # ==============================
    # PROMPT IA
    # ==============================

    mensajes = [

        {
            "role": "system",
            "content": f"""

Eres un coach bright Place Spot.

El cliente se llama: {nombre}

Su meta principal es:
{meta}

Ayudas personas a:
- ganar músculo
- ganar energía
- mejorar bienestar
- bajar nutrición

Tu enfoque está basado en:
- nutrición saludable
- batidos
- motivación
- bienestar
- productos Herbalife

Recomiendas productos Herbalife según la meta del cliente.

Hablas:
- positivo
- energético
- amigable
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

    # ==============================
    # RESPUESTA IA
    # ==============================
    respuesta = generar_respuesta(
    mensajes,
    usuarios,
    user_id,
    save_users
)
  

    respuesta_final = f"""
🤖  {respuesta}

— Coach Alexandra
"""

    return respuesta_final
    
# =====================================
# RECORDATORIO AUTOMÁTICO
# =====================================

async def recordatorio(context: ContextTypes.DEFAULT_TYPE):

    print("🔥 RECORDATORIO EJECUTADO")

    usuarios = cargar_usuarios()

    for user_id in usuarios:

        try:

            await context.bot.send_message(
                chat_id=int(user_id),
                text="""
🌱 RECORDATORIO DEL DÍA

Tu salud es una inversión diaria 💚

🥤 Tus batidos y té están disponibles hoy en FitClub Nutrition.
"""
            )

            print(f"✅ Enviado a {user_id}")

        except Exception as e:

            print(f"❌ Error enviando mensaje a {user_id}: {e}")

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
    ["🥤 Productos", "📈 Mi progreso"],
    ["✅ Registrar visita", "🏆 Mis puntos"],
    ["⏰ Recordatorios", "🕒 Horarios"],
    ["🤝 Negocio Herbalife", "👤 Mi cuenta"],
    ["📍 Dirección Club", "🛒 Hacer pedido"],
    ["📞 Contacto Coach"],
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

Bienvenido a Bright Place Spot
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


    # =====================================
    # MENU PRODUCTOS
    # =====================================

    if texto == "🥤 Productos":

        keyboard_productos = [
        ["🥤 Formula 1"],
        ["🫖 Herbal Tea"],
        ["💪 Proteína"],
        ["💊 Multivitamínico"],
        ["⬅️ Volver al menú"]
    ]

        reply_markup = ReplyKeyboardMarkup(
                keyboard_productos,
                resize_keyboard=True
            )

        await update.message.reply_text(
            "🥤 Selecciona un producto:",
            reply_markup=reply_markup
        )

        return


    # =====================================
    # VOLVER AL MENU
    # =====================================

    if texto == "⬅️ Volver al menú":

        keyboard = [
            ["🥤 Productos", "📈 Mi progreso"],
            ["✅ Registrar visita", "🏆 Mis puntos"],
            ["⏰ Recordatorios", "🕒 Horarios"],
            ["🤝 Negocio Herbalife", "🛒 Hacer pedido"],
            ["👤 Mi cuenta"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🏠 Menú principal",
            reply_markup=reply_markup
        )

        return
    
    # =========================================
    # FORMULA 1
    # =========================================


    elif texto == "🥤 Formula 1":

        await update.message.reply_text(
            """
    🥤 FORMULA 1 SHAKE

    El batido más popular de Herbalife 🌟

    ✅ BENEFICIOS:
    • Ayuda al control de peso
    • Nutrición balanceada
    • Energía para el día
    • Rico en proteína y fibra
    • Ayuda a reducir antojos

    💪 IDEAL PARA:
    • Bajar peso
    • Mantenerte saludable
    • Reemplazar comidas rápidas
    • Personas ocupadas

    🥄 SABORES DISPONIBLES:
    • Chocolate 🍫
    • Vainilla 🍦
    • Fresa 🍓
    • Cookies 🍪

    ⏰ CÓMO TOMARLO:
    1-2 veces al día

    🥛 PREPARACIÓN:
    • 2 cucharadas Formula 1
    • 8oz de agua o leche
    • Mezclar en shaker

    🔥 TIP COACH ALEXANDRA:
    Combínalo con proteína para mejores resultados.

    ⭐ Producto estrella de Bright Place Spot
    """
        )

        return
    

# =========================================
    # HERBAL TEA
    # =========================================



    elif texto == "🍵 Herbal Tea":

        await update.message.reply_text(
            """
    🍵 HERBAL TEA CONCENTRATE

    Tu boost natural de energía ⚡

    ✅ BENEFICIOS:
    • Más energía
    • Mayor enfoque mental
    • Ayuda al metabolismo
    • Menos cansancio
    • Ayuda a quemar calorías

    🔥 PERFECTO PARA:
    • Antes de entrenar
    • Empezar el día activo
    • Combatir fatiga
    • Trabajar con energía

    ☀️ SABORES:
    • Original
    • Limón 🍋
    • Durazno 🍑
    • Frambuesa 🍓

    ⏰ CÓMO TOMARLO:
    1-2 veces al día

    🥤 PREPARACIÓN:
    • 1/2 cucharadita
    • Agua caliente o fría

    ⚡ TIP COACH ALEXANDRA:
    Combínalo con Aloe Herbal para mejor digestión.

    🚀 Energía limpia sin azúcar excesiva
    """
        )

        return

    # =========================================
    # PROTEINA
    # =========================================


    elif texto == "💪 Proteína":

        await update.message.reply_text(
            """
    💪 PROTEÍNA PERSONALIZADA

    Recuperación y fuerza muscular 🔥

    ✅ BENEFICIOS:
    • Recuperación muscular
    • Ganancia muscular
    • Más saciedad
    • Mantiene masa muscular
    • Ayuda después del ejercicio

    🏋️ IDEAL PARA:
    • Ganar músculo
    • Recuperación
    • Deportistas
    • Personas activas

    🥛 CÓMO USARLA:
    • En batidos
    • Después de entrenar
    • Entre comidas

    ⏰ RECOMENDADO:
    1-2 veces al día

    🔥 TIP COACH ALEXANDRA:
    Agrégala a tu Formula 1 para mayor proteína y nutrición.

    ⭐ Excelente para transformación corporal
    """
        )

        return

   # =====================================
# MULTIVITAMINICO
# =====================================

    elif texto == "💊 Multivitamínico":

        await update.message.reply_text(
            """
    💊 MULTIVITAMÍNICO HERBALIFE

    Nutrición completa para tu cuerpo 🌿

    ✅ BENEFICIOS:
    • Vitaminas esenciales
    • Más energía
    • Sistema inmune
    • Bienestar general
    • Apoya metabolismo

    🛡️ AYUDA A:
    • Reducir fatiga
    • Mejorar nutrición
    • Complementar alimentación
    • Mantener salud diaria

    ⏰ CÓMO TOMARLO:
    1 tableta diaria

    🥗 RECOMENDADO PARA:
    • Hombres
    • Mujeres
    • Personas activas
    • Nutrición diaria

    🔥 TIP COACH ALEXANDRA:
    Úsalo diariamente junto a tu programa Herbalife.

    ⭐ Base nutricional inteligente
    """
        )

        return

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
    🥤 MENÚ

    • Formula 1
    • Herbal Tea
    • Proteína
    • Multivitamínico
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

    respuesta_ia = await responder_ia(update, user_id, texto)

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


order_handler = ConversationHandler(

    entry_points=[

        MessageHandler(
            filters.Regex("^🛒 Hacer pedido$"),
            start_order
        ),

        CommandHandler(
            "pedido",
            start_order
        ),
    ],

    states={

        PRODUCT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_product
            )
        ],

        QUANTITY: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_quantity
            )
        ],

        NOTE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                finish_order
            )
        ],
    },

    fallbacks=[
        CommandHandler("cancel", cancelar)
    ]
)
# =====================================
# HANDLERS
# =====================================

app.add_handler(conv_handler)

app.add_handler(order_handler)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        responder
    )
)

app.add_handler(CommandHandler("clientes", clientes_command))
app.add_handler(CommandHandler("stats", stats_command))
app.add_handler(CommandHandler("cliente", cliente_command))

app.add_handler(
    CommandHandler(
        "broadcast_inactivos",
        broadcast_inactivos
    )
)

app.add_handler(
    CommandHandler(
        "broadcast_objetivo",
        broadcast_objetivo
    )
)

app.add_handler(
    CommandHandler(
        "crear_campana_inactivos",
        crear_campana_inactivos
    )
)

app.add_handler(
    CommandHandler("broadcast", broadcast)
)


app.add_handler(
    CommandHandler(
        "reactivar_inactivos",
        reactivar_inactivos
    )
)

app.add_handler(
    CommandHandler(
        "campanas",
        ver_campanas
    )
)

app.add_handler(
    CommandHandler(
        "top_clientes",
        top_clientes
    )
)

app.add_handler(
    CommandHandler(
        "dar_puntos",
        dar_puntos
    )
)

app.add_handler(
    CommandHandler(
        "recordatorio",
        configurar_recordatorios
    )
)
# =========================================
# RECORDATORIOS
# =========================================

job_queue = app.job_queue

# MAÑANA ☀️
job_queue.run_daily(
    recordatorio,
    time=time(hour=7, minute=0)
)

# NOCHE 🌙
job_queue.run_daily(
    recordatorio,
    time=time(hour=19, minute=0)
)

job_queue.run_daily(
    revisar_inactivos,
    time=time(hour=12, minute=0),
)

print("🤖 BOT ENCENDIDO")

app.run_polling(drop_pending_updates=True)



# =====================================
# RUN
# =====================================
