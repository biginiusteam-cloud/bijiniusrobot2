import os
from dotenv import load_dotenv

load_dotenv()  # allows local .env in dev; on Koyeb/Render just use env vars panel

class Config:
    # Telegram API (get from https://my.telegram.org)
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")

    # Bot token (from @BotFather)
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # Force-subscribe channel (username like @mychannel OR numeric ID like -100123...)
    FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "")  # e.g. @MyUpdatesChannel or -1001234567890

    # Private database channel (must be numeric ID starting with -100; add your bot as admin)
    DATABASE_CHANNEL = int(os.getenv("DATABASE_CHANNEL", "0"))

    # MongoDB (Atlas or free Mongo service)
    MONGO_URL = os.getenv("MONGO_URL", "")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "biginusbot")

    # Admin user IDs (comma separated: "123,456")
    ADMINS = {int(x) for x in os.getenv("ADMINS", "").split(",") if x.strip().isdigit()}

    # Auto-delete (minutes). 0 = disabled. Can be changed at runtime with /autodelete
    AUTO_DELETE_MINUTES_DEFAULT = int(os.getenv("AUTO_DELETE_MINUTES", "0"))

    # Media shown on /start (optional)
    WELCOME_PHOTO_URL = os.getenv("WELCOME_PHOTO_URL", "")  # direct URL or leave empty

    # Misc
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
