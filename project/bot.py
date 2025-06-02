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

✅ Final Version of bot.py

import logging import os import re import phonenumbers import pandas as pd from aiogram import Bot, Dispatcher, executor, types from aiogram.types import InputFile from io import BytesIO

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # 🔁 Replace with your actual bot token logging.basicConfig(level=logging.INFO) bot = Bot(token=API_TOKEN) dp = Dispatcher(bot)

user_settings = {}

def get_user_settings(uid): if uid not in user_settings: user_settings[uid] = { "country_code": "BD", "format": "xlsx", "start": 1, "end": None } return user_settings[uid]

def extract_numbers(text): return re.findall(r'+?\d{7,15}', text)

def format_number(number, country_code="BD"): try: parsed = phonenumbers.parse(number, country_code) if phonenumbers.is_valid_number(parsed): return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164) except: pass return None

def process_numbers(numbers, country_code): formatted = set() for number in numbers: num = format_number(number, country_code) if num: formatted.add(num) return sorted(list(formatted))

def export_to_file(numbers, format): output = BytesIO() if format == "xlsx": df = pd.DataFrame({"Phone Numbers": numbers}) df.to_excel(output, index=False) output.seek(0) return output, "output.xlsx" elif format == "csv": df = pd.DataFrame({"Phone Numbers": numbers}) df.to_csv(output, index=False) output.seek(0) return output, "output.csv" elif format == "txt": output.write("\n".join(numbers).encode()) output.seek(0) return output, "output.txt" elif format == "vcf": vcf_data = "" for i, number in enumerate(numbers): vcf_data += f"BEGIN:VCARD\nVERSION:3.0\nFN:Contact {i+1}\nTEL:{number}\nEND:VCARD\n" output.write(vcf_data.encode()) output.seek(0) return output, "contacts.vcf" return None, None

@dp.message_handler(commands=['start']) async def start_handler(message: types.Message): get_user_settings(message.from_user.id) await message.reply("👋 নমস্কার! নম্বর ফরম্যাটার বটে আপনাকে স্বাগতম! ফাইল পাঠান অথবা /help লিখুন।")

@dp.message_handler(commands=['help']) async def help_handler(message: types.Message): await message.reply("""📌 কমান্ডসমূহ: /country BD বা US বা IN /format xlsx
