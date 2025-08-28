import os
import re

class Config:
    # Required env vars
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", ""))
    API_HASH = os.environ.get("API_HASH", "")
    MONGO_URL = os.environ.get("MONGO_URL", "")

    # Your Telegram database channel ID (add bot as admin there)
    # Example: -1001234567890
    DATABASE_CHANNEL = int(os.environ.get("DATABASE_CHANNEL", "-1002275599146"))

    # Welcome image URL
    WELCOME_PIC = os.environ.get("WELCOME_PIC", "https://envs.sh/F-V.jpg")

    # Regex used to extract Unique ID from your channel message
    # Matches things like: "🆔 Unique ID: 246810121" (case-insensitive, flexible spaces)
    UNIQUE_ID_REGEX = re.compile(r"(?i)unique\s*id\s*[:\-]\s*([A-Za-z0-9_\-\.]+)")

    # ---------------- NEW SETTINGS ---------------- #
    AUTO_DELETE_TIME = 0  # default 0 = disabled

    # Force-subscribe channel
    # Use numeric ID (like -1001234567890) or channel username ("@mychannel")
    FORCE_CHANNEL = os.environ.get("FORCE_CHANNEL", "-1002914520230")

    # Admin users (comma separated IDs in env)
    ADMINS = []
    _admins_raw = os.environ.get("ADMINS", "7547946252,7881272094")
    if _admins_raw:
        try:
            ADMINS = [int(x.strip()) for x in _admins_raw.split(",") if x.strip()]
        except Exception:
            ADMINS = []

    # Delay between messages when broadcasting (to avoid flood limits)
    BROADCAST_DELAY = float(os.environ.get("BROADCAST_DELAY", "0.05"))
