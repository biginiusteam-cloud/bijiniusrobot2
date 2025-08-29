from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pyrogram import Client
from config import Config

async def ensure_force_sub(client: Client, user_id: int) -> bool:
    """
    Returns True if user is a member of FORCE_SUB_CHANNEL, else sends prompt & returns False.
    """
    try:
        # If FORCE_SUB_CHANNEL is a string username, Pyrogram accepts it directly.
        await client.get_chat_member(Config.FORCE_SUB_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        # Not a member – prompt to join
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{str(Config.FORCE_SUB_CHANNEL).lstrip('@')}" )],
             [InlineKeyboardButton("✅ I Joined, Check Again", callback_data="fs_check_again")]]
        )
        await client.send_message(user_id,
            "Please join our channel first to use this bot.",
            reply_markup=kb
        )
        return False
    except Exception:
        # If channel is private and given as numeric ID, still works if bot is admin there.
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Open Channel", url=f"https://t.me/{str(Config.FORCE_SUB_CHANNEL).lstrip('@')}")]]
        )
        await client.send_message(user_id,
            "I couldn't verify your subscription right now. Please join the channel and try again.",
            reply_markup=kb
        )
        return False
