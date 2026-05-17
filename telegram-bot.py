import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import anthropic

# ── Sozlamalar (Environment Variables) ──────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Foydalanuvchi ma'lumotlari
user_histories: dict[int, list[dict]] = {}
user_languages: dict[int, str] = {}
user_modes: dict[int, str] = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

MESSAGES = {
    "uz": {
        "welcome": "Salom, {name}! 👋\n\nMen Claude AI asosidagi aqlli botman!\n\n📌 Buyruqlar:\n/start — Botni qayta ishga tushirish\n/clear — Suhbat tarixini tozalash\n/help — Yordam\n/lang — Tilni ozgartirish\n/mode — Rejimni ozgartirish\n/summarize — Suhbatni xulosalab ber",
        "help": "Bot Claude AI yordamida ishlaydi.\n\nBuyruqlar:\n/start /clear /help /lang /mode /summarize\n\nRejimlar:\nOddiy, Dasturchi, Yozuvchi, Oqituvchi",
        "cleared": "✅ Suhbat tarixi tozalandi!",
        "choose_lang": "🌍 Tilni tanlang:",
        "lang_set": "✅ Til ozgartirildi!",
        "choose_mode": "🎯 Rejimni tanlang:",
        "mode_set": "✅ Rejim ozgartirildi!",
        "error": "⚠️ Xatolik yuz berdi. Qayta urinib koring.",
        "summarize": "📝 Suhbat xulosasi:",
        "no_history": "Hali suhbat yoq.",
    },
    "ru": {
        "welcome": "Привет, {name}! 👋\n\nЯ умный бот на основе Claude AI!\n\n📌 Команды:\n/start /clear /help /lang /mode /summarize",
        "help": "Бот работает на Claude AI.\n\nКоманды:\n/start /clear /help /lang /mode /summarize\n\nРежимы:\nОбычный, Программист, Писатель, Учитель",
        "cleared": "✅ История очищена!",
        "choose_lang": "🌍 Выберите язык:",
        "lang_set": "✅ Язык изменён!",
        "choose_mode": "🎯 Выберите режим:",
        "mode_set": "✅ Режим изменён!",
        "error": "⚠️ Произошла ошибка. Попробуйте ещё раз.",
        "summarize": "📝 Краткое резюме:",
        "no_history": "История пуста.",
    },
    "en": {
        "welcome": "Hello, {name}! 👋\n\nI'm a smart bot powered by Claude AI!\n\n📌 Commands:\n/start /clear /help /lang /mode /summarize",
        "help": "Bot powered by Claude AI.\n\nCommands:\n/start /clear /help /lang /mode /summarize\n\nModes:\nNormal, Developer, Writer, Teacher",
        "cleared": "✅ History cleared!",
        "choose_lang": "🌍 Choose language:",
        "lang_set": "✅ Language changed!",
        "choose_mode": "🎯 Select mode:",
        "mode_set": "✅ Mode changed!",
        "error": "⚠️ An error occurred. Please try again.",
        "summarize": "📝 Conversation summary:",
        "no_history": "No conversation history yet.",
    },
}

MODE_PROMPTS = {
    "normal": "Siz foydali, aqlli va dostona AI yordamchisiz. Foydalanuvchi bilan uning tilida gaplashing.",
    "developer": "Siz tajribali dasturchi va texnik mutaxasssissiz. Kod yozishda va texnik savollarga javob berishda yordam bering. Kodlarni toliq va izohlar bilan yozing.",
    "writer": "Siz professional yozuvchi va muharrirsiz. Matn yozishda, tarjima qilishda yordam bering. Ijodiy va sifatli matnlar yarating.",
    "teacher": "Siz sabr-toqatli va malakali oqituvchisiz. Har qanday mavzuni oddiy va tushunarli tarzda tushuntiring. Misollar ishlating.",
}


def get_lang(user_id):
    return user_languages.get(user_id, "uz")


def get_mode(user_id):
    return user_modes.get(user_id, "normal")


def msg(user_id, key):
    return MESSAGES[get_lang(user_id)][key]


def get_history(user_id):
    return user_histories.setdefault(user_id, [])


def add_to_history(user_id, role, content):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    if len(history) > 30:
        user_histories[user_id] = history[-30:]


def ask_claude(user_id, user_message):
    add_to_history(user_id, "user", user_message)
    mode = get_mode(user_id)
    system_prompt = MODE_PROMPTS[mode]
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=get_history(user_id),
    )
    reply = response.content[0].text
    add_to_history(user_id, "assistant", reply)
    return reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    await update.message.reply_text(msg(user_id, "welcome").format(name=name))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(msg(user_id, "help"))


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text(msg(user_id, "cleared"))


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [[
        InlineKeyboardButton("🇺🇿 Ozbek", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    ]]
    await update.message.reply_text(msg(user_id, "choose_lang"), reply_markup=InlineKeyboardMarkup(keyboard))


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton("🎯 Oddiy / Normal", callback_data="mode_normal")],
        [InlineKeyboardButton("👨‍💻 Dasturchi / Developer", callback_data="mode_developer")],
        [InlineKeyboardButton("✍️ Yozuvchi / Writer", callback_data="mode_writer")],
        [InlineKeyboardButton("🎓 Oqituvchi / Teacher", callback_data="mode_teacher")],
    ]
    await update.message.reply_text(msg(user_id, "choose_mode"), reply_markup=InlineKeyboardMarkup(keyboard))


async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history = get_history(user_id)
    if not history:
        await update.message.reply_text(msg(user_id, "no_history"))
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-10:]])
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": f"Quyidagi suhbatni qisqa xulosalab ber:\n\n{history_text}"}],
        )
        summary = response.content[0].text
        await update.message.reply_text(f"{msg(user_id, 'summarize')}\n\n{summary}")
    except Exception as e:
        logger.error(f"Summarize xato: {e}")
        await update.message.reply_text(msg(user_id, "error"))


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if query.data.startswith("lang_"):
        user_languages[user_id] = query.data.split("_")[1]
        await query.edit_message_text(msg(user_id, "lang_set"))
    elif query.data.startswith("mode_"):
        user_modes[user_id] = query.data.split("_")[1]
        await query.edit_message_text(msg(user_id, "mode_set"))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = ask_claude(user_id, user_text)
        if len(reply) > 4096:
            for i in range(0, len(reply), 4096):
                await update.message.reply_text(reply[i:i+4096])
        else:
            await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text(msg(user_id, "error"))


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("mode", mode_command))
    app.add_handler(CommandHandler("summarize", summarize_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot ishga tushdi! ✅")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
