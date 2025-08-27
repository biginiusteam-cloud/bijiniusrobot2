from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from pymongo import MongoClient, ASCENDING
from config import Config

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
        # Ignore unrelated messages to keep UX clean
        return

    unique_id = message.text.strip()
    rec = messages_col.find_one({"unique_id": unique_id})

    if rec:
        # Send back the exact stored message text
        await message.reply_text(rec["message_text"], quote=True)
    else:
        await message.reply_text(
            "❌ Sorry, no status found for this ID.\n"
            "Please check your Unique ID and try again.",
            quote=True
        )

    # Clear state
    states_col.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"state": "idle"}},  # or delete if you prefer
        upsert=True
    )
