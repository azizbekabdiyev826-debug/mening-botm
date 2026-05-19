import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Loglarni tekshirish uchun sozlama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Assalomu alaykum! Bot muvaffaqiyatli ishlamoqda!')

def main() -> None:
    # Skrinshotingizda ko'ringan shaxsiy bot tokeningiz
    BOT_TOKEN = "7334469733:AAFlp4lBcl0lQoE7MYWtM23L0cTgsYFfGgY"

    # Yangi python-telegram-bot v20.x arxitekturasi
    application = Application.builder().token(BOT_TOKEN).build()

    # /start buyrug'ini ulaymiz
    application.add_handler(CommandHandler("start", start))

    # Botni fonda doimiy ishlatish buyrug'i
    print("Bot muvaffaqiyatli ishga tushirildi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
