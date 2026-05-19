import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ==============================
# TOKEN
# ==============================
BOT_TOKEN = "8901962433:AAHniqqn0bzFMneW42mu7MYWtM23L0cTgsY"

# API KEYS (bepul ro'yxatdan o'ting)
WEATHER_API = "your_openweathermap_api_key"   # openweathermap.org
NEWS_API    = "your_newsapi_key"              # newsapi.org
EXCHANGE_API = "your_exchangerate_api_key"    # exchangerate-api.com

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# /start
# ==============================
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

# ==============================
# CALLBACK HANDLER
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "valyuta":
        await query.edit_message_text(
            "💱 *Valyuta kurslari (USD bazasida):*\n\n"
            "Kurs olish uchun: /kurs yozing\n"
            "Masalan: `/kurs USD UZS 100`",
            parse_mode="Markdown"
        )

    elif data == "obhavo":
        await query.edit_message_text(
            "🌤 *Ob-havo*\n\n"
            "Shahar nomini yuboring:\n"
            "Masalan: `/obhavo Toshkent`",
            parse_mode="Markdown"
        )

    elif data == "namoz":
        await query.edit_message_text(
            "🕌 *Namoz vaqtlari*\n\n"
            "Shahar yozing:\n"
            "Masalan: `/namoz Toshkent`",
            parse_mode="Markdown"
        )

    elif data == "yangiliklar":
        await get_news(query)

    elif data == "ai":
        await query.edit_message_text(
            "🤖 *AI Suhbat*\n\n"
            "Istalgan savolingizni yozing, javob beraman!\n"
            "Masalan: `Inson miyasi qancha og'ir?`",
            parse_mode="Markdown"
        )
        context.user_data["mode"] = "ai"

    elif data == "konvertor":
        await query.edit_message_text(
            "💰 *Valyuta Konvertori*\n\n"
            "Format: `/konvert 100 USD UZS`",
            parse_mode="Markdown"
        )

    elif data == "hikmat":
        hikmatlar = [
            "Bilim — eng katta boylik. 📖",
            "Sabr — zafarning kaliti. 🏆",
            "Yaxshi inson bo'l, qolganini vaqt hal qiladi. ⏳",
            "Har bir qiyinchilik — yangi imkoniyat. 💪",
            "Ota-onangni hurmat qil — bu eng ulug' burch. ❤️",
            "Kamtar bo'l, chunki er ostida yotganlar ham bir vaqt bosh ko'targan. 🌱",
        ]
        import random
        await query.edit_message_text(f"📖 *Bugungi hikmat:*\n\n_{random.choice(hikmatlar)}_", parse_mode="Markdown")

    elif data == "retsept":
        await query.edit_message_text(
            "🍽 *Retsept*\n\n"
            "Ovqat nomini yozing:\n"
            "Masalan: `/retsept osh`",
            parse_mode="Markdown"
        )

    elif data == "tarjimon":
        await query.edit_message_text(
            "🌐 *Tarjimon*\n\n"
            "Format: `/tarjima [matn]`\n"
            "Masalan: `/tarjima salom dunyo`",
            parse_mode="Markdown"
        )

    elif data == "kalkul":
        await query.edit_message_text(
            "🧮 *Kalkulyator*\n\n"
            "Format: `/hisob [ifoda]`\n"
            "Masalan: `/hisob 150 * 12 + 500`",
            parse_mode="Markdown"
        )

    elif data == "eslatma":
        await query.edit_message_text(
            "⏰ *Eslatma*\n\n"
            "Format: `/eslatma [daqiqa] [xabar]`\n"
            "Masalan: `/eslatma 30 Dori ichish vaqti`",
            parse_mode="Markdown"
        )

    elif data == "tugkun":
        await query.edit_message_text(
            "🎂 *Tug'ilgan kun eslatmasi*\n\n"
            "Format: `/tugkun [ism] [kun.oy]`\n"
            "Masalan: `/tugkun Alibek 15.06`",
            parse_mode="Markdown"
        )

    elif data == "xarid":
        await query.edit_message_text(
            "🛒 *Xarid ro'yxati*\n\n"
            "• `/qosh [mahsulot]` — qo'shish\n"
            "• `/royxat` — ko'rish\n"
            "• `/tozala` — tozalash",
            parse_mode="Markdown"
        )

    elif data == "kaloriya":
        await query.edit_message_text(
            "🏋 *Kaloriya hisoblagich*\n\n"
            "Format: `/kaloriya [ovqat nomi]`\n"
            "Masalan: `/kaloriya osh`",
            parse_mode="Markdown"
        )

    elif data == "sport":
        await query.edit_message_text(
            "⚽ *Sport yangiliklari*\n\n"
            "/sport yozing — so'nggi natijalar",
            parse_mode="Markdown"
        )

    elif data == "ingliz":
        await query.edit_message_text(
            "📚 *Ingliz tili*\n\n"
            "/soz — bugungi yangi so'z\n"
            "/test — mini test",
            parse_mode="Markdown"
        )

    elif data == "quiz":
        await get_quiz(query)

    elif data == "tarix":
        await get_tarix(query)

    elif data == "buyurtma":
        await query.edit_message_text(
            "🛍 *Buyurtma berish*\n\n"
            "Format: `/buyurtma [mahsulot nomi]`\n"
            "Masalan: `/buyurtma Pizza 2ta`",
            parse_mode="Markdown"
        )

    elif data == "hazil":
        hazillar = [
            "Dasturchi xotiniga: 'Bozorga bor, bir litr sut ol, tuxum bo'lsa 6ta ol.' Xotin 6 litr sut olib keldi. 😄",
            "— Matematik sevgilisiga: 'Seni cheksiz sevaман!' — Sevgilisi: 'Isbotla!' — Matematik: '∞' 💝",
            "Nega dasturchilar ko'zoynak taqadi? Chunki C sharp (C#) ko'rmaydi! 😂",
        ]
        import random
        await query.edit_message_text(f"😂 *Hazil:*\n\n{random.choice(hazillar)}", parse_mode="Markdown")

    elif data == "film":
        filmlar = [
            "🎬 *Interstellar* (2014) — Kosmik sarguzasht",
            "🎬 *The Shawshank Redemption* (1994) — Umid haqida",
            "🎬 *Inception* (2010) — Ong ichida ong",
            "🎬 *The Dark Knight* (2008) — Betman",
            "🎬 *Forrest Gump* (1994) — Hayot haqida",
        ]
        import random
        await query.edit_message_text(f"🎬 *Bugungi film tavsiyasi:*\n\n{random.choice(filmlar)}", parse_mode="Markdown")

    elif data == "musiqa":
        musiqalar = [
            "🎵 Lofi hip-hop — ishlaganda tinglash uchun",
            "🎵 Shodiyona — O'zbek klassikasi",
            "🎵 Yulduz Usmonova — Muhabbat qo'shiqlari",
            "🎵 Jasur Urinov — Zamonaviy o'zbek",
        ]
        import random
        await query.edit_message_text(f"🎵 *Musiqa tavsiyasi:*\n\n{random.choice(musiqalar)}", parse_mode="Markdown")

    elif data == "parol":
        import random, string
        chars = string.ascii_letters + string.digits + "!@#$%"
        parol = ''.join(random.choice(chars) for _ in range(16))
        await query.edit_message_text(
            f"🔒 *Yangi kuchli parol:*\n\n`{parol}`\n\n_Saqlang va hech kimga bermang!_",
            parse_mode="Markdown"
        )

    elif data == "crypto":
        await get_crypto(query)

# ==============================
# YANGILIKLAR
# ==============================
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
            await query.edit_message_text("❌ Yangiliklar topilmadi. NEWS_API kalitini tekshiring.")
    except:
        await query.edit_message_text("❌ Xatolik. NEWS_API kalitini sozlang.")

# ==============================
# CRYPTO
# ==============================
async def get_crypto(query):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd"
        r = requests.get(url).json()
        text = (
            "₿ *Crypto narxlari (USD):*\n\n"
            f"🟡 Bitcoin: ${r['bitcoin']['usd']:,}\n"
            f"🔵 Ethereum: ${r['ethereum']['usd']:,}\n"
            f"🟢 Tether: ${r['tether']['usd']}\n"
        )
        await query.edit_message_text(text, parse_mode="Markdown")
    except:
        await query.edit_message_text("❌ Crypto ma'lumotlari yuklanmadi.")

# ==============================
# QUIZ
# ==============================
async def get_quiz(query):
    quizlar = [
        {"s": "O'zbekiston poytaxti?", "j": "Toshkent"},
        {"s": "Dunyo eng baland tog'i?", "j": "Everest"},
        {"s": "1+1=?", "j": "2"},
        {"s": "Quyosh sistemasida nechta sayyora bor?", "j": "8"},
        {"s": "Eng katta okean?", "j": "Tinch okean"},
    ]
    import random
    q = random.choice(quizlar)
    await query.edit_message_text(
        f"❓ *Quiz savoli:*\n\n{q['s']}\n\nJavob: ||{q['j']}||",
        parse_mode="MarkdownV2"
    )

# ==============================
# TARIX FAKTI
# ==============================
async def get_tarix(query):
    faktlar = [
        "📅 1991-yil 1-sentyabr — O'zbekiston mustaqillikka erishdi!",
        "📅 1969-yil 20-iyul — Inson birinchi marta Oyga qadam qo'ydi.",
        "📅 1991-yil 25-dekabr — Sovet Ittifoqi rasman tarqab ketdi.",
        "📅 1945-yil 9-may — Ikkinchi Jahon urushi tugadi.",
        "📅 2001-yil 11-sentyabr — AQShda terrakt sodir bo'ldi.",
    ]
    import random
    await query.edit_message_text(random.choice(faktlar), parse_mode="Markdown")

# ==============================
# OB-HAVO
# ==============================
async def obhavo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Format: /obhavo Toshkent")
        return
    shahar = " ".join(context.args)
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={shahar}&appid={WEATHER_API}&units=metric&lang=ru"
        r = requests.get(url).json()
        if r.get("main"):
            temp = r["main"]["temp"]
            feels = r["main"]["feels_like"]
            hum = r["main"]["humidity"]
            desc = r["weather"][0]["description"]
            await update.message.reply_text(
                f"🌤 *{shahar} ob-havosi:*\n\n"
                f"🌡 Harorat: {temp}°C\n"
                f"🤔 His etiladi: {feels}°C\n"
                f"💧 Namlik: {hum}%\n"
                f"☁️ Holat: {desc}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Shahar topilmadi.")
    except:
        await update.message.reply_text("❌ WEATHER_API kalitini sozlang.")

# ==============================
# NAMOZ VAQTLARI
# ==============================
async def namoz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Format: /namoz Toshkent")
        return
    shahar = " ".join(context.args)
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        url = f"https://api.aladhan.com/v1/timingsByCity/{today}?city={shahar}&country=UZ&method=3"
        r = requests.get(url).json()
        if r.get("data"):
            t = r["data"]["timings"]
            await update.message.reply_text(
                f"🕌 *{shahar} namoz vaqtlari:*\n\n"
                f"🌅 Bomdod: {t['Fajr']}\n"
                f"☀️ Quyosh: {t['Sunrise']}\n"
                f"🕛 Peshin: {t['Dhuhr']}\n"
                f"🌇 Asr: {t['Asr']}\n"
                f"🌆 Shom: {t['Maghrib']}\n"
                f"🌙 Xufton: {t['Isha']}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Shahar topilmadi.")
    except:
        await update.message.reply_text("❌ Xatolik yuz berdi.")

# ==============================
# KALKULYATOR
# ==============================
async def hisob_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Format: /hisob 100 * 12")
        return
    ifoda = " ".join(context.args)
    try:
        natija = eval(ifoda)
        await update.message.reply_text(f"🧮 {ifoda} = *{natija}*", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Noto'g'ri ifoda.")

# ==============================
# ESLATMA
# ==============================
async def eslatma_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Format: /eslatma 30 Dori ichish vaqti")
        return
    try:
        daqiqa = int(context.args[0])
        xabar = " ".join(context.args[1:])
        await update.message.reply_text(f"⏰ {daqiqa} daqiqadan keyin eslataman: *{xabar}*", parse_mode="Markdown")
        context.job_queue.run_once(
            lambda ctx: ctx.bot.send_message(update.effective_chat.id, f"🔔 Eslatma: {xabar}"),
            daqiqa * 60
        )
    except:
        await update.message.reply_text("❌ Xatolik. Format: /eslatma 30 Xabar matni")

# ==============================
# XARID RO'YXATI
# ==============================
shopping_lists = {}

async def qosh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Format: /qosh Non")
        return
    item = " ".join(context.args)
    shopping_lists.setdefault(uid, []).append(item)
    await update.message.reply_text(f"✅ *{item}* ro'yxatga qo'shildi!", parse_mode="Markdown")

async def royxat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    items = shopping_lists.get(uid, [])
    if not items:
        await update.message.reply_text("🛒 Ro'yxat bo'sh.")
        return
    text = "🛒 *Xarid ro'yxati:*\n\n"
    for i, item in enumerate(items, 1):
        text += f"{i}. {item}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def tozala_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    shopping_lists[uid] = []
    await update.message.reply_text("✅ Ro'yxat tozalandi!")

# ==============================
# PAROL GENERATOR
# ==============================
async def parol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random, string
    chars = string.ascii_letters + string.digits + "!@#$%"
    parol = ''.join(random.choice(chars) for _ in range(16))
    await update.message.reply_text(f"🔒 *Yangi parol:*\n\n`{parol}`", parse_mode="Markdown")

# ==============================
# ODDIY XABAR HANDLER (AI mode)
# ==============================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mode = context.user_data.get("mode", "")

    if mode == "ai":
        await update.message.reply_text(
            "🤖 AI javob:\n\n"
            "Hozircha AI moduli sozlanmoqda. "
            "OpenAI API kalitini qo'shing va to'liq ishlaydi!"
        )
    else:
        await update.message.reply_text(
            "Menyu uchun /start yozing! 😊"
        )

# ==============================
# MAIN
# ==============================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("obhavo", obhavo_cmd))
    app.add_handler(CommandHandler("namoz", namoz_cmd))
    app.add_handler(CommandHandler("hisob", hisob_cmd))
    app.add_handler(CommandHandler("eslatma", eslatma_cmd))
    app.add_handler(CommandHandler("qosh", qosh_cmd))
    app.add_handler(CommandHandler("royxat", royxat_cmd))
    app.add_handler(CommandHandler("tozala", tozala_cmd))
    app.add_handler(CommandHandler("parol", parol_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ SmartBot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
