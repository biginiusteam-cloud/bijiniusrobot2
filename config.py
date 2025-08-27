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
    DATABASE_CHANNEL = int(os.environ.get("DATABASE_CHANNEL", "-1002828848208"))

    # Welcome image URL
    WELCOME_PIC = os.environ.get("WELCOME_PIC", "https://envs.sh/F-V.jpg")

    # Regex used to extract Unique ID from your channel message
    # Matches things like: "🆔 Unique ID: 246810121" (case-insensitive, flexible spaces)
    UNIQUE_ID_REGEX = re.compile(r"(?i)unique\s*id\s*[:\-]\s*([A-Za-z0-9_\-\.]+)")
