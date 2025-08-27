from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

@Client.on_message(filters.command(["start"]) & filters.private)
async def start_message(client, message):
    buttons = [
        [InlineKeyboardButton("🔎 Check Status", callback_data="check_status")]
    ]

    await message.reply_photo(
        photo=Config.WELCOME_PIC,
        caption=(
            "👋 <b>Welcome!</b>\n\n"
            "Tap the button below to check your status."
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command(["help"]) & filters.private)
async def help_message(client, message):
    await message.reply_text(
        "ℹ️ <b>How it works</b>\n\n"
        "1) Tap <b>Check Status</b>\n"
        "2) Send your <b>Unique ID</b>\n"
        "3) I’ll send back the exact status message saved for your ID.",
    )
