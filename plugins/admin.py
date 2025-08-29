import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from datetime import datetime, timedelta
from config import Config

# connect to mongo
mongo = MongoClient(Config.MONGO_URL) if Config.MONGO_URL else None
db = mongo.get_database("scholarship_bot") if mongo else None
users = db.users if db else None
settings = db.settings if db else None   # new collection for global settings

ADMINS = Config.ADMINS or []
BROADCAST_DELAY = float(Config.BROADCAST_DELAY or 0.05)
FORCE_CHANNEL = Config.FORCE_CHANNEL

# ------------------ /stats ------------------
@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_handler(client: Client, message: Message):
    if not users:
        await message.reply_text("⚠️ Database not configured.")
        return

    total_users = users.count_documents({})
    active_since = datetime.utcnow() - timedelta(days=30)
    active_users = users.count_documents({"last_active": {"$gte": active_since}})
    blocked_users = users.count_documents({"blocked": True})
    inactive_estimate = total_users - active_users

    text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: <b>{total_users}</b>\n"
        f"✅ Active (30 days): <b>{active_users}</b>\n"
        f"🚫 Blocked users (marked): <b>{blocked_users}</b>\n"
        f"⚠️ Inactive (no activity 30d): <b>{inactive_estimate}</b>\n"
    )
    await message.reply_text(text)

# ------------------ /broadcast ------------------
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_start(client: Client, message: Message):
    """
    Usage: reply to a message with /broadcast
    The replied message will be copied to all users in the DB.
    """
    if not users:
        await message.reply_text("⚠️ Database not configured.")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a message with /broadcast to send it to all users.")
        return

    confirm = await message.reply_text(
        "Are you sure you want to broadcast this message to all users?\n"
        "Reply with 'yes' to confirm or anything else to cancel."
    )

    try:
        reply = await client.listen(chat_id=message.chat.id, filters=filters.text & filters.user(ADMINS), timeout=30)
    except Exception:
        await confirm.edit_text("Broadcast cancelled (no confirmation).")
        return

    if reply.text.lower() != "yes":
        await confirm.edit_text("Broadcast cancelled.")
        return

    await confirm.edit_text("Broadcast started. Sending messages...")

    sent = 0
    failed = 0

    cursor = users.find({})
    async for user_doc in cursor:
        uid = user_doc.get("user_id")
        try:
            # copy the replied message to user
            await message.reply_to_message.copy(uid)
            sent += 1
            # small delay to avoid flood limits
            await asyncio.sleep(BROADCAST_DELAY)
        except Exception:
            failed += 1
            try:
                users.update_one({"user_id": uid}, {"$set": {"blocked": True}})
            except Exception:
                pass

    await confirm.edit_text(f"✅ Broadcast finished.\n\nSent: {sent}\nFailed: {failed}")

# ------------------ Auto-delete command ------------------
@Client.on_message(filters.command("autodelete") & filters.user(ADMINS))
async def set_autodelete(client: Client, message: Message):
    """
    Usage: /autodelete <minutes>
    Example: /autodelete 60   → delete messages after 60 minutes
             /autodelete 0    → disable auto-delete
    """
    if not settings:
        await message.reply_text("⚠️ Database not configured.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            current = settings.find_one({"_id": "autodelete"}) or {"value": 0}
            await message.reply_text(f"ℹ️ Current auto-delete is <b>{current['value']}</b> minutes (0 = disabled).")
            return

        minutes = int(parts[1])
        settings.update_one({"_id": "autodelete"}, {"$set": {"value": minutes}}, upsert=True)

        if minutes == 0:
            await message.reply_text("🛑 Auto-delete disabled (messages will not be deleted).")
        else:
            await message.reply_text(f"✅ Auto-delete enabled. Messages will be deleted after {minutes} minutes.")

    except ValueError:
        await message.reply_text("⚠️ Please provide a valid number (minutes).")

# ------------------ Callback handler for 'I've Joined' button ------------------
@Client.on_callback_query(filters.regex(r"^force_sub_check$"))
async def on_force_check(client, callback_query):
    user_id = callback_query.from_user.id
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        if member.status in ("member", "administrator", "creator"):
            await callback_query.answer("✅ You are a member now. You can continue.", show_alert=True)
            await callback_query.message.delete()
            return
    except Exception:
        pass
    await callback_query.answer("🚫 Not a member yet. Please join the channel first.", show_alert=True)
