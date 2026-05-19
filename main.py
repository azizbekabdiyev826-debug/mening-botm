import logging
import requests
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ==============================
# TOKEN (Railway o'zgaruvchisidan xavfsiz o'qiydi)
# ==============================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8901962433:AAHniqqn0bzFMneW42mu7MYWtM23L0cTgsY")

# API KEYS
WEATHER_API = "your_openweathermap_api_key"
NEWS_API    = "your_newsapi_key"
EXCHANGE_API = "your_exchangerate_api_key"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💱 Valyuta kursi", callback_data="valyuta"),
         InlineKeyboardButton("🌤 Ob-havo", callback_data="obhavo")],
        [InlineKeyboardButton("🕌 Namoz vaqtlari", callback_data="namoz"),
         InlineKeyboardButton("📰 Yangiliklar", callback_data="yangiliklar")],
        [InlineKeyboardButton("🤖 AI suhbat", callback_data="ai"),
         InlineKeyboardButton("💰 Konvertor", callback_data="konvertor")],
        [InlineKeyboardButton("📖 Hikmat", callback_data="hikmat"),
         InlineKeyboardButton("🍽 Retsept", callback_data="retsept")],
        [InlineKeyboardButton("🌐 Tarjimon", callback_data="tarjimon"),
         InlineKeyboardButton("🧮 Kalkulyator", callback_data="kalkul")],
        [InlineKeyboardButton("⏰ Eslatma", callback_data="eslatma"),
         InlineKeyboardButton("🎂 Tug'ilgan kun", callback_data="tugkun")],
        [InlineKeyboardButton("🛒 Xarid ro'yxati", callback_data="xarid"),
         InlineKeyboardButton("🏋 Kaloriya", callback_data="kaloriya")],
        [InlineKeyboardButton("⚽ Sport", callback_data="sport"),
         InlineKeyboardButton("📚 Ingliz tili", callback_data="ingliz")],
        [InlineKeyboardButton("❓ Quiz", callback_data="quiz"),
         InlineKeyboardButton("📅 Tarix fakti", callback_data="tarix")],
        [InlineKeyboardButton("🛍 Buyurtma", callback_data="buyurtma"),
         InlineKeyboardButton("😂 Hazil", callback_data="hazil")],
        [InlineKeyboardButton("🎬 Film tavsiya", callback_data="film"),
         InlineKeyboardButton("🎵 Musiqa", callback_data="musiqa")],
        [InlineKeyboardButton("🔒 Parol gen.", callback_data="parol"),
         InlineKeyboardButton("₿ Crypto", callback_data="crypto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 *SmartBot* ga xush kelibsiz!\n\n"
        "Quyidagi funksiyalardan birini tanlang:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "valyuta":
        await query.edit_message_text("💱 *Valyuta kurslari (USD bazasida):*\n\nKurs olish uchun: /kurs yozing\nMasalan: `/kurs USD UZS 100`", parse_mode="Markdown")
    elif data == "obhavo":
        await query.edit_message_text("🌤 *Ob-havo*\n\nShahar nomini yuboring:\nMasalan: `/obhavo Toshkent`", parse_mode="Markdown")
    elif data == "namoz":
        await query.edit_message_text("🕌 *Namoz vaqtlari*\n\nShahar yozing:\nMasalan: `/namoz Toshkent`", parse_mode="Markdown")
    elif data == "yangiliklar":
        await get_news(query)
    elif data == "ai":
        await query.edit_message_text("🤖 *AI Suhbat*\n\nIstalgan savolingizni yozing, javob beraman!\nMasalan: `Inson miyasi qancha og'ir?`", parse_mode="Markdown")
        context.user_data["mode"] = "ai"
    elif data == "konvertor":
        await query.edit_message_text("💰 *Valyuta Konvertori*\n\nFormat: `/konvert 100 USD UZS`", parse_mode="Markdown")
    elif data == "hikmat":
        hikmatlar = ["Bilim — eng katta boylik. 📖", "Sabr — zafarning kaliti. 🏆", "Yaxshi inson bo'l, qolganini vaqt hal qiladi. ⏳"]
        import random
        await query.edit_message_text(f"📖 *Bugungi hikmat:*\n\n_{random.choice(hikmatlar)}_", parse_mode="Markdown")
    elif data == "retsept":
        await query.edit_message_text("🍽 *Retsept*\n\nOvqat nomini yozing:\nMasalan: `/retsept osh`", parse_mode="Markdown")
    elif data == "tarjimon":
        await query.edit_message_text("🌐 *Tarjimon*\n\nFormat: `/tarjima [matn]`\nMasalan: `/tarjima salom dunyo`", parse_mode="Markdown")
    elif data == "kalkul":
        await query.edit_message_text("🧮 *Kalkulyator*\n\nFormat: `/hisob [ifoda]`\nMasalan: `/hisob 150 * 12 + 500`", parse_mode="Markdown")
    elif data == "eslatma":
        await query.edit_message_text("⏰ *Eslatma*\n\nFormat: `/eslatma [daqiqa] [xabar]`\nMasalan: `/eslatma 30 Dori ichish vaqti`", parse_mode="Markdown")
    elif data == "tugkun":
        await query.edit_message_text("🎂 *Tug'ilgan kun eslatmasi*\n\nFormat: `/tugkun [ism] [kun.oy]`\nMasalan: `/tugkun Alibek 15.06`", parse_mode="Markdown")
    elif data == "xarid":
        await query.edit_message_text("🛒 *Xarid ro'yxati*\n\n• `/qosh [mahsulot]` — qo'shish\n• `/royxat` — ko'rish", parse_mode="Markdown")
    elif data == "kaloriya":
        await query.edit_message_text("🏋 *Kaloriya hisoblagich*\n\nFormat: `/kaloriya [ovqat nomi]`\nMasalan: `/kaloriya osh`", parse_mode="Markdown")
    elif data == "sport":
        await query.edit_message_text("⚽ *Sport yangiliklari*\n\n/sport yozing — so'nggi natijalar", parse_mode="Markdown")
    elif data == "ingliz":
        await query.edit_message_text("📚 *Ingliz tili*\n\n/soz — bugungi yangi so'z", parse_mode="Markdown")
    elif data == "quiz":
        await get_quiz(query)
    elif data == "tarix":
        await get_tarix(query)
    elif data == "buyurtma":
        await query.edit_message_text("🛍 *Buyurtma berish*\n\nFormat: `/buyurtma [mahsulot nomi]`\nMasalan: `/buyurtma Pizza 2ta`", parse_mode="Markdown")
    elif data == "hazil":
        hazillar = ["Nega dasturchilar ko'zoynak taqadi? Chunki C sharp (C#) ko'rmaydi! 😂"]
        import random
        await query.edit_message_text(f"😂 *Hazil:*\n\n{random.choice(hazillar)}", parse_mode="Markdown")
    elif data == "film":
        filmlar = ["🎬 *Interstellar* (2014) — Kosmik sarguzasht"]
        import random
        await query.edit_message_text(f"🎬 *Bugungi film tavsiyasi:*\n\n{random.choice(filmlar)}", parse_mode="Markdown")
    elif data == "musiqa":
        musiqalar = ["🎵 Lofi hip-hop — ishlaganda tinglash uchun"]
        import random
        await query.edit_message_text(f"🎵 *Musiqa tavsiyasi:*\n\n{random.choice(musiqalar)}", parse_mode="Markdown")
    elif data == "parol":
        import random, string
        chars = string.ascii_letters + string.digits + "!@#$%"
        parol = ''.join(random.choice(chars) for _ in range(16))
        await query.edit_message_text(f"🔒 *Yangi kuchli parol:*\n\n`{parol}`", parse_mode="Markdown")
    elif data == "crypto":
        await get_crypto(query)

async def get_news(query):
    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API}"
        r = requests.get(url).json()
        if r.get("articles"):
            text = "📰 *Dunyo yangiliklari:*\n\n"
            for i, a in enumerate(r["articles"][:5], 1):
                text += f"{i}. {a['title']}\n\n"
            await query.edit_message_text(text, parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ Yangiliklar yuklanmadi.")
    except:
        await query.edit_message_text("❌ Xatolik yuz berdi.")

async def get_crypto(query):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd"
        r = requests.get(url).json()
        text = f"₿ *Crypto narxlari (USD):*\n\n🟡 Bitcoin: ${r['bitcoin']['usd']:,}\n🔵 Ethereum: ${r['ethereum']['usd']:,}\n"
        await query.edit_message_text(text, parse_mode="Markdown")
    except:
        await query.edit_message_text("❌ Crypto ma'lumotlari yuklanmadi.")

async def get_quiz(query):
    await query.edit_message_text("❓ *Savol:* O'zbekiston poytaxti?\n\nJavob: Toshkent", parse_mode="Markdown")

async def get_tarix(query):
    await query.edit_message_text("📅 1991-yil 1-sentyabr — O'zbekiston mustaqillikka erishdi!", parse_mode="Markdown")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Menyu uchun /start yozing! 😊")

def main():
    if not BOT_TOKEN:
        print("❌ Xatolik: BOT_TOKEN aniqlanmadi!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("✅ SmartBot muvaffaqiyatli ishlamoqda!")
    app.run_polling()

if __name__ == "__main__":
    main()
