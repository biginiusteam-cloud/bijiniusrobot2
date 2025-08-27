import datetime
from pyrogram import Client, filters
from pymongo import MongoClient, ASCENDING
from config import Config

mongo = MongoClient(Config.MONGO_URL)
db = mongo["StatusBot"]
messages_col = db["messages"]

# Ensure indexes exist
messages_col.create_index([("unique_id", ASCENDING)], unique=True)

def extract_unique_id(text: str):
    """
    Pulls the Unique ID out of a message using the regex in Config.
    Returns the ID string or None.
    """
    if not text:
        return None
    m = Config.UNIQUE_ID_REGEX.search(text)
    if not m:
        return None
    return m.group(1).strip()

# Save NEW posts in your database channel
@Client.on_message(filters.channel & filters.chat(Config.DATABASE_CHANNEL))
async def save_new_channel_post(client, message):
    text = message.text or message.caption
    uid = extract_unique_id(text)
    if not uid:
        return  # message doesn’t contain a recognizable "Unique ID: ..."
    messages_col.update_one(
        {"unique_id": uid},
        {
            "$set": {
                "unique_id": uid,
                "message_text": text,
                "updated_at": datetime.datetime.utcnow()
            },
            "$setOnInsert": {"created_at": datetime.datetime.utcnow()}
        },
        upsert=True
    )
    print(f"✅ Saved/updated status for ID: {uid}")

# Save EDITS too (in case you fix typos or add info)
@Client.on_edited_message(filters.channel & filters.chat(Config.DATABASE_CHANNEL))
async def save_edited_channel_post(client, message):
    text = message.text or message.caption
    uid = extract_unique_id(text)
    if not uid:
        return
    messages_col.update_one(
        {"unique_id": uid},
        {
            "$set": {
                "unique_id": uid,
                "message_text": text,
                "updated_at": datetime.datetime.utcnow()
            },
            "$setOnInsert": {"created_at": datetime.datetime.utcnow()}
        },
        upsert=True
    )
    print(f"✏️ Updated status for ID: {uid} (edited)")
