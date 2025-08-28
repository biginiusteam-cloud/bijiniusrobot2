from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from pyrogram.errors import UserNotParticipant

# Force subscribe check
async def check_force_subscribe(client, user_id):
    try:
        member = await client.get_chat_member(Config.FORCE_CHANNEL, user_id)
        if member.status in ("kicked", "left"):
            return False
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True  # if something goes wrong, don’t block the user

@Client.on_message(filters.command(["start"]) & filters.private)
async def start_message(client, message):
    user_id = message.from_user.id
    if Config.FORCE_CHANNEL:
        in_channel = await check_force_subscribe(client, user_id)
        if not in_channel:
            join_button = InlineKeyboardMarkup(
                [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{(await client.get_chat(Config.FORCE_CHANNEL)).username}")]]
            )
            return await message.reply_text(
                "⚠️ You must join our channel first to use this bot.",
                reply_markup=join_button
            )

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
