import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from .logger import log

def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMINS

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(
        "**User Commands**\n"
        "/start – Welcome + Check Status button\n\n"
        "**Admin Commands**\n"
        "/broadcast <text> – Send to all users\n"
        "/stats – Show total users\n"
        "/autodelete <minutes> – Set minutes (0 = disable)\n"
    )

@Client.on_message(filters.command("autodelete"))
async def autodelete_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) == 1 or not parts[1].isdigit():
        await message.reply_text("Usage: `/autodelete <minutes>` (0 disables)", quote=True)
        return

    minutes = int(parts[1])
    await client.col_settings.update_one(
        {"key": "autodelete_minutes"},
        {"$set": {"value": minutes}},
        upsert=True
    )
    await message.reply_text(f"Auto-delete set to **{minutes}** minute(s).")

@Client.on_message(filters.command("stats"))
async def stats_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        return
    total = await client.col_users.count_documents({})
    await message.reply_text(f"**Stats**\nTotal users: **{total}**")

@Client.on_message(filters.command("broadcast"))
async def broadcast_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        await message.reply_text("Usage: `/broadcast <text>`", quote=True)
        return

    text = parts[1]
    sent = 0
    total = 0
    async for u in client.col_users.find({}, {"user_id": 1}):
        total += 1
        try:
            await client.send_message(u["user_id"], text)
            sent += 1
            await asyncio.sleep(0.05)  # be gentle
        except Exception:
            pass

    await message.reply_text(f"Broadcast done. Sent {sent}/{total}.")
