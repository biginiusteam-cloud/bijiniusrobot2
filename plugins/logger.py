from pyrogram import Client, filters
from pymongo import MongoClient
from datetime import datetime
from config import Config

# Connect to Mongo (each plugin opens its own short connection — ok for small bots)
mongo = MongoClient(Config.MONGO_URL) if Config.MONGO_URL else None
db = mongo.get_database("scholarship_bot") if mongo else None
users = db.users if db else None

@Client.on_message(filters.private)
async def save_user_info(client: Client, message):
    """
    Runs on every private message and upserts user info with last_active timestamp.
    """
    if not users:
        return

    user = message.from_user
    doc = {
        "user_id": user.id,
        "username": getattr(user, "username", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "last_active": datetime.utcnow(),
        # keep a 'blocked' flag default False; we'll set to True if messages fail in broadcast
        "blocked": False,
    }
    users.update_one({"user_id": user.id}, {"$set": doc}, upsert=True)
