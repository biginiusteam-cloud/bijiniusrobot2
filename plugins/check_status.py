from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from pymongo import MongoClient, ASCENDING
from config import Config
import asyncio

# Import global auto delete time from autodelete.py
try:
    from .autodelete import AUTO_DELETE_TIME
except ImportError:
    AUTO_DELETE_TIME = 0  # fallback if not loaded

mongo = MongoClient(Config.MONGO_URL)
db = mongo["StatusBot"]
messages_col = db["messages"]       # stores {unique_id, message_text, created_at}
states_col = db["user_states"]      # stores {user_id, state}

# Helpful indexes (safe to run many times)
messages_col.create_index([("unique_id", ASCENDING)], unique=True)
states_col.create_index([("user_id", ASCENDING)], unique=True)

@Client.on_callback_query(filters.regex("^check_status$"))
async def ask_unique_id(client: Client, cq: CallbackQuery):
    await cq.message.reply_text("✍️ Please send me your <b>Unique ID</b>.", quote=True)
    states_col.update_one(
        {"user_id": cq.from_user.id},
        {"$set": {"state": "waiting_for_id"}},
        upsert=True
    )
    await cq.answer()

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def receive_unique_id(client: Client, message: Message):
    # Only act if user previously pressed "Check Status"
    st = states_col.find_one({"user_id": message.from_user.id})
    if not st or st.get("state") != "waiting_for_id":
        return

    unique_id = message.text.strip()
    rec = messages_col.find_one({"unique_id": unique_id})

    if rec:
        sent = await message.reply_text(rec["message_text"], quote=True)

        # Auto-delete after time if enabled
        if AUTO_DELETE_TIME > 0:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await sent.delete()
                await message.delete()
            except Exception:
                pass

    else:
        sent = await message.reply_text(
            "❌ Sorry, no status found for this ID.\n"
            "Please check your Unique ID and try again.",
            quote=True
        )
        if AUTO_DELETE_TIME > 0:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await sent.delete()
                await message.delete()
            except Exception:
                pass

    # Clear state
    states_col.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"state": "idle"}},
        upsert=True
    )
