from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config
from .force_subscribe import ensure_force_sub
from .logger import log

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message):
    user_id = message.from_user.id

    # Register user in DB
    await client.col_users.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id}},
        upsert=True
    )

    # Force-subscribe check
    if not await ensure_force_sub(client, user_id):
        return

    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Check Status", callback_data="check_status")]]
    )

    if Config.WELCOME_PHOTO_URL:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=Config.WELCOME_PHOTO_URL,
            caption="Welcome! Tap **Check Status** to get your latest update.",
            reply_markup=kb
        )
    else:
        await client.send_message(
            chat_id=message.chat.id,
            text="Welcome! Tap **Check Status** to get your latest update.",
            reply_markup=kb
        )

@Client.on_callback_query(filters.regex("^fs_check_again$"))
async def fs_check_again(client: Client, cq: CallbackQuery):
    if await ensure_force_sub(client, cq.from_user.id):
        await cq.message.edit_text("Thanks for joining! Tap the button below:",
                                   reply_markup=InlineKeyboardMarkup(
                                       [[InlineKeyboardButton("✅ Check Status", callback_data="check_status")]]
                                   ))
    else:
        await cq.answer("Still not joined. Please join the channel.", show_alert=True)
