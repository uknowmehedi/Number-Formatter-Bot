from telegram import Update
from telegram.ext import ContextTypes

user_settings = {}

async def set_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_settings[update.effective_user.id] = {'country_code': context.args[0]}
        await update.message.reply_text(f"Country code set to: {context.args[0]}")
    else:
        await update.message.reply_text("Usage: /country +880")