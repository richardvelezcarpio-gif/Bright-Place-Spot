from telegram import Update
from telegram.ext import ContextTypes

import openai
import os

ADMIN_ID = "7816979989"

openai.api_key = os.getenv("OPENAI_API_KEY")


async def crear_campana_inactivos(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = str(update.effective_user.id)

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ No autorizado"
        )

        return

    prompt = """
Crea un mensaje corto y motivacional
para clientes fitness que no entrenan
hace varios días.

Debe ser:
- emocional
- energético
- amigable
- con CTA
- máximo 40 palabras
"""

    respuesta = openai.ChatCompletion.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": "Eres experto en fitness marketing"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    mensaje = respuesta.choices[0].message.content

    await update.message.reply_text(
        f"🤖 Campaña generada:\n\n{mensaje}"
    )