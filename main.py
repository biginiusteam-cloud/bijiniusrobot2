import logging
from pyrogram import Client
from config import Config

# Basic sanity checks – fail fast if something crucial is missing.
missing = []
if not Config.BOT_TOKEN: missing.append("BOT_TOKEN")
if not Config.API_ID: missing.append("API_ID")
if not Config.API_HASH: missing.append("API_HASH")
if not Config.MONGO_URL: missing.append("MONGO_URL")
if not str(Config.DATABASE_CHANNEL).startswith("-100"):
    print("Warning: DATABASE_CHANNEL should look like -100XXXXXXXXXX")

if missing:
    raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("status-bot")

# Create the Pyrogram bot client and auto-load plugins from the "plugins" package
app = Client(
    name="status-bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins"),
    in_memory=True  # no local session files needed
)

if __name__ == "__main__":
    logger.info("Starting bot…")
    app.run()
