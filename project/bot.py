from telegram.ext import Application, CommandHandler
from handlers.start_handler import start
from handlers.country_handler import set_country
from handlers.format_handler import set_format

TOKEN = "YOUR_BOT_TOKEN"

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("country", set_country))
    app.add_handler(CommandHandler("format", set_format))

✅ Main Function
if name == "main":
    app = Application.builder().token(TOKEN).build()
    setup_handlers(app)
    app.run_polling()

    ✅ bot.py - Telegram Number Formatter Bot (Supports Groups, File Cleanup)

from telegram import Update from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes from utils.file_utils import export_to_file, cleanup_file import os

TOKEN = "YOUR_BOT_TOKEN_HERE"  # 🔁 আপনার বট টোকেন এখানে বসান

✅ START command

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("👋 স্বাগতম! একটি নাম্বার পাঠান বা ফাইল দিন ফরম্যাট করার জন্য।")

✅ TEXT or FILE handler

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE): text = update.message.text # 👉 এখানে নাম্বার এক্সট্রাকশন ও ফরম্যাটিং যুক্ত করুন numbers = list(set(text.split()))  # ডেমো: word গুলো আলাদা করে নিচ্ছে

if not numbers:
    await update.message.reply_text("❗ কোনো ফোন নম্বর পাওয়া যায়নি।")
    return

# ✅ এক্সপোর্ট করুন ফাইলে
user_id = update.effective_user.id
export_format = "xlsx"
file_path = export_to_file(numbers, export_format, f"data/output_{user_id}")

await update.message.reply_document(document=open(file_path, "rb"))

# ✅ STEP 8: ফাইল ডিলিট করুন
cleanup_file(file_path)

✅ FILE Upload (TXT/XLSX etc.) handler

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE): file = await update.message.document.get_file() file_path = f"data/temp_{update.effective_user.id}_{file.file_unique_id}" await file.download_to_drive(file_path)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

numbers = list(set(content.split()))
export_format = "csv"
export_file = export_to_file(numbers, export_format, f"data/output_{update.effective_user.id}")
await update.message.reply_document(document=open(export_file, "rb"))

cleanup_file(file_path)
cleanup_file(export_file)