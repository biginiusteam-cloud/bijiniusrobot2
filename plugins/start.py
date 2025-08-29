from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient
import asyncio

# Mongo setup
mongo = MongoClient(Config.MONGO_URL) if Config.MONGO_URL else None
db = mongo.get_database("scholarship_bot") if mongo else None
settings = db.settings if db else None

# Get auto-delete time (default 0 = no delete)
def get_auto_delete_time():
    if settings:
        doc = settings.find_one({"_id": "auto_delete"})
        if doc:
            return int(doc.get("time", 0))
    return 0

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
            sent = await message.reply_text(
                "⚠️ You must join our channel first to use this bot.",
                reply_markup=join_button
            )
            # auto delete check
            delete_time = get_auto_delete_time()
            if delete_time > 0:
                await asyncio.sleep(delete_time)
                await sent.delete()
                await message.delete()
            return

    buttons = [
        [InlineKeyboardButton("🔎 Check Status", callback_data="check_status")]
    ]

    sent = await message.reply_photo(
        photo=Config.WELCOME_PIC,
        caption=(
            "👋 <b>Welcome!</b>\n\n"
            "Tap the button below to check your status."
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    # auto delete check
    delete_time = get_auto_delete_time()
    if delete_time > 0:
        await asyncio.sleep(delete_time)
        await sent.delete()
        await message.delete()

@Client.on_message(filters.command(["help"]) & filters.private)
async def help_message(client, message):
    sent = await message.reply_text(
        "ℹ️ <b>How it works</b>\n\n"
        "1) Tap <b>Check Status</b>\n"
        "2) Send your <b>Unique ID</b>\n"
        "3) I’ll send back the exact status message saved for your ID.",
    )
    # auto delete check
    delete_time = get_auto_delete_time()
    if delete_time > 0:
        await asyncio.sleep(delete_time)
        await sent.delete()
        await message.delete()
