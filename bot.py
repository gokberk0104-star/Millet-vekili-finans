
import os
import logging
import requests

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

logging.basicConfig(level=logging.INFO)

# TRON ağı
TRON_API = "https://api.trongrid.io"
USDT_CONTRACT = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"

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
        "TRX ve USDT cüzdan sistemine hoş geldiniz.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "wallet":
        address = context.user_data.get("tron_address")

        if address:
            await query.message.reply_text(
                f"💰 CÜZDANIM\n\n"
                f"Adres: {address}\n\n"
                "Bakiyeyi görmek için /bakiye yazın."
            )
        else:
            context.user_data["waiting_address"] = True
            await query.message.reply_text(
                "🔗 TronLink cüzdan adresini gönder.\n\n"
                "Yalnızca T ile başlayan herkese açık adresini gönder.\n"
                "Özel anahtarını veya kurtarma kelimelerini ASLA gönderme."
            )

    elif query.data == "deposit":
        await query.message.reply_text(
            "📥 Para yatırma paneli hazırlanıyor."
        )

    elif query.data == "send":
        await query.message.reply_text(
            "📤 Güvenli transfer paneli hazırlanıyor."
        )

    elif query.data == "history":
        await query.message.reply_text(
            "📜 İşlem geçmişi hazırlanıyor."
        )


async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_address"):
        return

    address = update.message.text.strip()

    if not address.startswith("T") or len(address) != 34:
        await update.message.reply_text(
            "Geçerli bir TRON adresi gir. Adres T ile başlamalıdır."
        )
        return

    context.user_data["tron_address"] = address
    context.user_data["waiting_address"] = False

    await update.message.reply_text(
        "✅ Cüzdan adresin kaydedildi.\n\n"
        "Bakiyeni görmek için /bakiye yaz."
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = context.user_data.get("tron_address")

    if not address:
        await update.message.reply_text(
            "Önce Cüzdanım bölümünden adresini kaydet."
        )
        return

    try:
        response = requests.post(
            f"{TRON_API}/wallet/getaccount",
            json={"address": address, "visible": True},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        trx = data.get("balance", 0) / 1_000_000

        token_response = requests.post(
            f"{TRON_API}/wallet/triggerconstantcontract",
            json={
                "owner_address": address,
                "contract_address": USDT_CONTRACT,
                "function_selector": "balanceOf(address)",
                "parameter": address_parameter(address),
                "visible": True
            },
            timeout=15
        )
        token_response.raise_for_status()
        token_data = token_response.json()

        result = token_data.get("constant_result", [])
        usdt = int(result[0], 16) / 1_000_000 if result else 0

        await update.message.reply_text(
            f"💰 CÜZDAN BAKİYESİ\n\n"
            f"TRX: {trx:.6f}\n"
            f"USDT: {usdt:.6f}\n\n"
            f"Adres: {address}"
        )

    except Exception:
        logging.exception("Bakiye sorgulama hatası")
        await update.message.reply_text(
            "Bakiye şu anda alınamadı. Biraz sonra tekrar dene."
        )


def address_parameter(address):
    import base58
    import binascii

    decoded = base58.b58decode_check(address)
    hex_address = decoded.hex()[2:]
    return hex_address.rjust(64, "0")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("Bot tokeni bulunamadı.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bakiye", balance))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)
    )

    app.run_polling()


if __name__ == "__main__":
    main()

