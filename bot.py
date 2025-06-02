import os
import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)
import pandas as pd
from io import BytesIO

logging.basicConfig(level=logging.INFO)
user_settings = {}

def get_user_settings(uid):
    if uid not in user_settings:
        user_settings[uid] = {'lang': 'bn', 'code': '+880', 'range': (1, 100000), 'format': 'xlsx'}
    return user_settings[uid]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 হ্যালো! আমি নাম্বার ফরম্যাট করব। আপনি:\n"
        "- /setcode +91\n"
        "- /setrange 1 100\n"
        "- /language en বা bn\n"
        "- /format xlsx, txt, csv, vcf"
    )

async def setcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = get_user_settings(uid)
    if context.args:
        settings['code'] = context.args[0]
        await update.message.reply_text(f"✅ Country code set: {context.args[0]}")
    else:
        await update.message.reply_text("⚠️ Please provide a code, e.g., /setcode +91")

async def setrange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = get_user_settings(uid)
    try:
        start = int(context.args[0])
        end = int(context.args[1])
        settings['range'] = (start, end)
        await update.message.reply_text(f"✅ Range set: {start}-{end}")
    except:
        await update.message.reply_text("⚠️ Please provide valid range, e.g., /setrange 1 100")

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = get_user_settings(uid)
    lang = context.args[0] if context.args else "bn"
    settings['lang'] = lang
    await update.message.reply_text(f"✅ Language set to: {lang}")

async def format_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = get_user_settings(uid)
    fmt = context.args[0] if context.args else "xlsx"
    settings['format'] = fmt
    await update.message.reply_text(f"✅ Output format set to: {fmt}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = get_user_settings(uid)
    code = settings['code']
    numbers = [code + ''.join(filter(str.isdigit, x)) for x in update.message.text.split()]
    numbers = list(dict.fromkeys(numbers))
    await send_file(update, numbers, settings['format'])

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = get_user_settings(uid)
    code = settings['code']
    file = await update.message.document.get_file()
    file_bytes = BytesIO()
    await file.download_to_memory(out=file_bytes)
    file_bytes.seek(0)

    if update.message.document.file_name.endswith(".xlsx"):
        df = pd.read_excel(file_bytes, header=None)
    else:
        df = pd.read_csv(file_bytes, header=None)

    start, end = settings['range']
    numbers = df.iloc[start-1:end, 0].astype(str).apply(lambda x: code + ''.join(filter(str.isdigit, x))).tolist()
    numbers = list(dict.fromkeys(numbers))
    await send_file(update, numbers, settings['format'])

async def send_file(update, numbers, fmt):
    if fmt == "xlsx":
        df = pd.DataFrame(numbers)
        output = BytesIO()
        df.to_excel(output, index=False, header=False)
        output.seek(0)
        await update.message.reply_document(document=InputFile(output, filename="formatted_numbers.xlsx"))
    elif fmt == "txt":
        output = BytesIO("\n".join(numbers).encode())
        await update.message.reply_document(document=InputFile(output, filename="formatted_numbers.txt"))
    elif fmt == "csv":
        output = BytesIO("\n".join(numbers).encode())
        await update.message.reply_document(document=InputFile(output, filename="formatted_numbers.csv"))
    elif fmt == "vcf":
        vcf_lines = [f"BEGIN:VCARD\nVERSION:3.0\nFN:{n}\nTEL:{n}\nEND:VCARD" for n in numbers]
        output = BytesIO("\n".join(vcf_lines).encode())
        await update.message.reply_document(document=InputFile(output, filename="contacts.vcf"))

    await update.message.reply_text(f"✅ মোট {len(numbers)}টি নাম্বার ফরম্যাট করা হয়েছে।")
    try:
    df = pd.read_csv(file_bytes, header=None)
except Exception as e:
    await update.message.reply_text("❌ ফাইল পড়া যায়নি, দয়া করে ফরম্যাট চেক করুন।")
    return


