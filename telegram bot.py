import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import anthropic

# ── Sozlamalar ──────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = "8970670423:AAF0iCJY28hbkFv8dQ4xKTsLvgnfXxQucj4"
ANTHROPIC_API_KEY = "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"

# Har foydalanuvchi uchun suhbat tarixi (xotira)
user_histories: dict[int, list[dict]] = {}

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Yordamchi funksiyalar ────────────────────────────────────────────────────
def get_history(user_id: int) -> list[dict]:
    """Foydalanuvchi suhbat tarixini qaytaradi."""
    return user_histories.setdefault(user_id, [])


def add_to_history(user_id: int, role: str, content: str):
    """Tarixga xabar qo'shadi (max 20 ta xabar)."""
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    # Xotira limitini saqlash
    if len(history) > 20:
        user_histories[user_id] = history[-20:]


def ask_claude(user_id: int, user_message: str) -> str:
    """Claude API ga so'rov yuboradi va javob qaytaradi."""
    add_to_history(user_id, "user", user_message)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=(
            "Siz foydali, aqlli va do'stona AI yordamchisiz. "
            "Foydalanuvchi bilan uning tilidxda gaplashing. "
            "Javoblaringiz aniq, qisqa va tushunarli bo'lsin."
        ),
        messages=get_history(user_id),
    )

    reply = response.content[0].text
    add_to_history(user_id, "assistant", reply)
    return reply


# ── Buyruqlar ────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ start buyrug'i."""
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Salom, {name}! 👋\n\n"
        "Men Claude AI asosidagi botman. Menga istalgan savolingizni yuboring!\n\n"
        "📌 Buyruqlar:\n"
        "/start — Botni qayta ishga tushirish\n"
        "/clear — Suhbat tarixini tozalash\n"
        "/help  — Yordam\n"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ help buyrug'i."""
    await update.message.reply_text(
        "🤖 *Bot haqida:*\n\n"
        "Bu bot Claude AI yordamida ishlaydi.\n"
        "Savolingizni yozing — javob olasiz!\n\n"
        "📌 *Buyruqlar:*\n"
        "/start — Botni ishga tushirish\n"
        "/clear — Suhbat tarixini tozalash\n"
        "/help  — Ushbu yordam xabari\n\n"
        "💡 *Misol:*\n"
        "• Python kodini tushuntir\n"
        "• Tarjima qil\n"
        "• Matn yoz\n"
        "• Savollarga javob ber",
        parse_mode="Markdown",
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ clear buyrug'i — tarixni tozalaydi."""
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("✅ Suhbat tarixi tozalandi. Yangi suhbat boshlang!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oddiy xabarlarni qayta ishlaydi."""
    user_id = update.effective_user.id
    user_text = update.message.text

    # "Yozmoqda..." ko'rsatish
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        reply = ask_claude(user_id, user_text)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        )


# ── Asosiy funksiya ──────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Buyruqlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))

    # Oddiy xabarlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi! ✅")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
