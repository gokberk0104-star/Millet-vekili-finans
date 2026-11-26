
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💰 Cüzdanım", callback_data="wallet"),
            InlineKeyboardButton("📥 Para Yatır", callback_data="deposit")
        ],
        [
            InlineKeyboardButton("📤 Para Gönder", callback_data="send"),
            InlineKeyboardButton("📜 İşlem Geçmişi", callback_data="history")
        ]
    ]

    await update.message.reply_text(
        "🏦 MİLLET VEKİLİ FİNANS\n\n"
        "TRX ve USDT cüzdan sistemine hoş geldiniz.\n\n"
        "İşlem yapmak için menüyü kullanın.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    messages = {
        "wallet": "💰 Cüzdan paneli yakında hazır olacak.",
        "deposit": "📥 Para yatırma sistemi hazırlanıyor.",
        "send": "📤 Güvenli transfer sistemi hazırlanıyor.",
        "history": "📜 İşlem geçmişi hazırlanıyor."
    }

    await query.message.reply_text(messages.get(query.data, "Geçersiz işlem."))

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Bot tokeni bulunamadı.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()

if __name__ == "__main__":
    main()
