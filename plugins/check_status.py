import asyncio
from datetime import datetime, timezone
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .force_subscribe import ensure_force_sub
from .logger import log

ASK_ID_STATE = {}  # simple in-memory state: user_id -> waiting bool

async def get_autodelete_minutes(client: Client) -> int:
    s = await client.col_settings.find_one({"key": "autodelete_minutes"})
    return int(s["value"]) if s and isinstance(s.get("value"), int) else 0

@Client.on_callback_query(filters.regex("^check_status$"))
async def on_check_status_click(client: Client, cq):
    user_id = cq.from_user.id
    if not await ensure_force_sub(client, user_id):
        await cq.answer("Please join the channel first.", show_alert=True)
        return
    ASK_ID_STATE[user_id] = True
    await cq.message.reply_text("Please enter your **Unique ID** (numbers only).")

@Client.on_message(filters.private & ~filters.command(["start", "help"]))
async def on_user_text(client: Client, message):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    if not ASK_ID_STATE.get(user_id):
        return  # ignore random messages unless they tapped Check Status

    if not text.isdigit():
        await message.reply_text("Unique ID must be numbers only. Try again.")
        return

    unique_id = text
    ASK_ID_STATE.pop(user_id, None)

    # Find latest status for that ID
    doc = await client.col_statuses.find_one(
        {"unique_id": unique_id},
        sort=[("timestamp", -1)]
    )

    if not doc:
        m = await message.reply_text(
            "No status found for this Unique ID yet. Please check later."
        )
        minutes = await get_autodelete_minutes(client)
        if minutes > 0:
            asyncio.create_task(_auto_delete(client, m.chat.id, m.id, minutes))
        return

    # Reply with the exact saved message text
    reply = await message.reply_text(doc["message_text"])

    # Auto-delete logic
    minutes = await get_autodelete_minutes(client)
    if minutes > 0:
        asyncio.create_task(_auto_delete(client, reply.chat.id, reply.id, minutes))

async def _auto_delete(client: Client, chat_id: int, msg_id: int, minutes: int):
    try:
        await asyncio.sleep(minutes * 60)
        await client.delete_messages(chat_id, msg_id)
    except Exception as e:
        log.warning(f"Auto-delete failed: {e}")
