import re
from datetime import datetime, timezone
from pyrogram import Client, filters
from config import Config
from .logger import log

# Regex to capture 🆔 Unique ID: 123456789 (digits only)
UID_REGEX = re.compile(r"🆔\s*Unique\s*ID:\s*(\d+)", re.IGNORECASE)

@Client.on_message(filters.channel & filters.chat(Config.DATABASE_CHANNEL))
async def capture_status_from_channel(client: Client, message):
    """
    Listens to new posts in your private DATABASE_CHANNEL.
    Extracts Unique ID and stores the full message in MongoDB.
    """
    if not message.text:
        return

    text = message.text
    m = UID_REGEX.search(text)
    if not m:
        log.info("Database channel post skipped (no Unique ID found).")
        return

    unique_id = m.group(1)
    doc = {
        "unique_id": unique_id,
        "message_text": text,
        "timestamp": datetime.now(timezone.utc),
        "message_id": message.id
    }

    await client.col_statuses.insert_one(doc)
    log.info(f"Saved status for Unique ID {unique_id} from channel post {message.id}")
