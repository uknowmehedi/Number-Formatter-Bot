import re
import pandas as pd
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

user_settings = {}

def format_number(number, code):
    number = re.sub(r'\D', '', number)
    if number.startswith('0'):
        return code + number[1:]
    elif number.startswith(code[1:]):
        return '+' + number
    elif number.startswith('+'):
        return number
    else:
        return code + number

def extract_numbers_from_text(text):
    return re.findall(r'\d{7,15}', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_settings.setdefault(uid, {'lang': 'bn', 'code': '+880', 'range': (1, 100000), 'format': 'xlsx'})
   await update.message.reply_text(
    "👋 হ্যালো! আমি নাম্বার ফরম্যাট করব। আপনি:\n"
    "- /setcode +91\n"
    "- /setrange 1 100\n"
    "- /language en বা bn\n"
    "- /format xlsx, txt, csv, vcf\n"
)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = context.args[0].lower() if context.args else 'bn'
    if lang in ['en', 'bn']:
        user_settings.setdefault(uid, {'lang': 'bn', 'code': '+880', 'range': (1, 100000), 'format': 'xlsx'})
        user_settings[uid]['lang'] = lang
        await update.message.reply_text("✅ ভাষা পরিবর্তন হয়েছে।" if lang == 'bn' else "✅ Language changed.")
    else:
        await update.message.reply_text("❌ Only 'en' or 'bn' allowed.")

async def set_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    code = context.args[0] if context.args else '+880'
    if code.startswith('+') and code[1:].isdigit():
        def get_user_settings(uid):
    if uid not in user_settings:
        user_settings[uid] = {'lang': 'bn', 'code': '+880', 'range': (1, 100000), 'format': 'xlsx'}
    return user_settings[uid]['code'] = code
        await update.message.reply_text(f"✅ দেশ কোড সেট করা হয়েছে: {code}")
    else:
        await update.message.reply_text("❌ সঠিক কোড দিন। যেমন: /setcode +880")

async def set_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if len(context.args) >= 2:
        try:
            start, end = int(context.args[0]), int(context.args[1])
            user_settings.setdefault(uid, {'lang': 'bn', 'code': '+880', 'range': (1, 100000), 'format': 'xlsx'})
            user_settings[uid]['range'] = (start, end)
            await update.message.reply_text(f"✅ সিরিয়াল সীমা নির্ধারিত: {start} - {end}")
        except:
            await update.message.reply_text("❌ সঠিকভাবে লিখুন: /setrange 1 100")
    else:
        await update.message.reply_text("❌ সঠিকভাবে লিখুন: /setrange 1 100")

async def set_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if context.args:
        fmt = context.args[0].lower()
        if fmt in ['xlsx', 'txt', 'csv', 'vcf']:
            user_settings.setdefault(uid, {'lang': 'bn', 'code': '+880', 'range': (1, 100000), 'format': 'xlsx'})
            user_settings[uid]['format'] = fmt
            await update.message.reply_text(f"✅ ফাইল ফরম্যাট সেট: {fmt}")
        else:
            await update.message.reply_text("❌ ফরম্যাট হতে হবে: xlsx, txt, csv, vcf")
    else:
        await update.message.reply_text("❌ উদাহরণ: /format xlsx")

async def process_and_send(update: Update, numbers, settings):
    numbers = list(dict.fromkeys(numbers))
    start, end = settings['range']
    numbers = numbers[start - 1:end]
    formatted = [format_number(num, settings['code']) for num in numbers]

    if not formatted:
        await update.message.reply_text("কোনো নাম্বার পাওয়া যায়নি।")
        return

    file_format = settings.get('format', 'xlsx')
    if file_format == 'txt':
        content = "\n".join(formatted)
        file = BytesIO(content.encode('utf-8'))
        file.name = 'formatted_numbers.txt'
    elif file_format == 'csv':
        df = pd.DataFrame({'Number': formatted})
        file = BytesIO()
        df.to_csv(file, index=False)
        file.seek(0)
        file.name = 'formatted_numbers.csv'
    elif file_format == 'vcf':
        content = ""
        for num in formatted:
            content += f"BEGIN:VCARD\nVERSION:3.0\nFN: {num[1:]}\nTEL:{num}\nEND:VCARD\n"
        file = BytesIO(content.encode('utf-8'))
        file.name = 'contacts.vcf'
    else:
        df = pd.DataFrame({'Number': formatted})
        file = BytesIO()
        df.to_excel(file, index=False)
        file.seek(0)
        file.name = 'formatted_numbers.xlsx'

    await update.message.reply_document(InputFile(file))
    await update.message.reply_text(f"✅ মোট {len(formatted)}টি নাম্বার ফরম্যাট করা হয়েছে।")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = user_settings.get(uid, {'code': '+880', 'range': (1, 100000), 'format': 'xlsx'})
    numbers = extract_numbers_from_text(update.message.text)
    await process_and_send(update, numbers, settings)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    settings = user_settings.get(uid, {'code': '+880', 'range': (1, 100000), 'format': 'xlsx'})
    file = await update.message.document.get_file()
    file_bytes = await file.download_as_bytearray()
    filename = update.message.document.file_name

    try:
        if filename.endswith('.txt'):
            text = file_bytes.decode('utf-8')
            numbers = extract_numbers_from_text(text)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file_bytes))
            text = df.astype(str).apply(' '.join, axis=1).str.cat(sep=' ')
            numbers = extract_numbers_from_text(text)
        else:
            await update.message.reply_text("❌ শুধু .txt বা .xlsx ফাইল দিন।")
            return

        await process_and_send(update, numbers, settings)

    except Exception as e:
        await update.message.reply_text(f"⚠️ সমস্যা হয়েছে: {str(e)}")

def main():
    app = ApplicationBuilder().token("Your_Bot_Token").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", set_language))
    app.add_handler(CommandHandler("setcode", set_code))
    app.add_handler(CommandHandler("setrange", set_range))
    app.add_handler(CommandHandler("format", set_format))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
