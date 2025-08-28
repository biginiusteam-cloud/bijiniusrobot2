from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
import asyncio

# If FORCE_CHANNEL is provided as username instead of ID, we'll attempt to use it as-is.
FORCE_CHANNEL = Config.FORCE_CHANNEL
ADMINS = Config.ADMINS or []

async def _is_subscribed(bot: Client, user_id: int) -> bool:
    """
    Returns True if user is a member of FORCE_CHANNEL.
    """
    if not FORCE_CHANNEL:
        # No force channel configured → treat as subscribed
        return True
    try:
        # get_chat_member accepts username or numeric ID
        member = await bot.get_chat_member(FORCE_CHANNEL, user_id)
        if member.status in ("member", "administrator", "creator"):
            return True
        return False
    except Exception:
        # Any error -> treat as not subscribed
        return False

@Client.on_message(filters.private & ~filters.user(ADMINS))
async def require_subscription_handler(client: Client, message):
    """
    Intercepts private messages and requires user to join FORCE_CHANNEL before proceeding.
    Uses continue_propagation() to allow other handlers to run if the user is subscribed.
    """
    # allow if admin or if channel not set
    if not FORCE_CHANNEL:
        return

    user_id = message.from_user.id
    if await _is_subscribed(client, user_id):
        # let other handlers process the message
        return

    # Build the join-button (if FORCE_CHANNEL is numeric ID and channel has username, try to fetch username)
    try:
        chat = await client.get_chat(FORCE_CHANNEL)
        if chat.username:
            url = f"https://t.me/{chat.username}"
        else:
            # fallback to using t.me/c/... only works for private channels; numeric id link may not be web friendly
            url = f"https://t.me/{chat.id}"
    except Exception:
        url = "https://t.me/"  # fallback

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📢 Join Channel", url=url)],
            [InlineKeyboardButton("✅ I've Joined", callback_data="force_sub_check")]
        ]
    )

    await message.reply_text(
        "⚠️ You must join our official channel to use this bot.\n\n"
        "Please join the channel and then press *I've Joined*.",
        reply_markup=keyboard,
        quote=True
    )
    # stop propagation: do not run other handlers until they join
    return
