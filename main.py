import logging
import asyncio
from pyrogram import Client
from config import Config
from motor.motor_asyncio import AsyncIOMotorClient

# --- Sanity checks
missing = []
if not Config.API_ID: missing.append("API_ID")
if not Config.API_HASH: missing.append("API_HASH")
if not Config.BOT_TOKEN: missing.append("BOT_TOKEN")
if not Config.MONGO_URL: missing.append("MONGO_URL")
if not Config.FORCE_SUB_CHANNEL: missing.append("FORCE_SUB_CHANNEL")
if not str(Config.DATABASE_CHANNEL).startswith("-100"):
    missing.append("DATABASE_CHANNEL (must be numeric and start with -100)")

if missing:
    raise SystemExit("Missing/invalid config: " + ", ".join(missing))

# --- Logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
log = logging.getLogger("biginusbot")

# --- Create bot client
app = Client(
    "biginusbot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins"),
    in_memory=True
)

# --- Attach DB and runtime settings to app for use in plugins
@app.on_start()
async def _on_start(_app: Client):
    log.info("Connecting to MongoDB...")
    _app.mongo = AsyncIOMotorClient(Config.MONGO_URL)
    _app.db = _app.mongo[Config.MONGO_DB_NAME]
    # collections
    _app.col_users = _app.db["users"]
    _app.col_statuses = _app.db["statuses"]
    _app.col_settings = _app.db["settings"]

    # Ensure indexes
    await _app.col_users.create_index("user_id", unique=True)
    await _app.col_statuses.create_index([("unique_id", 1), ("timestamp", -1)])
    await _app.col_settings.create_index("key", unique=True)

    # Ensure default autodelete setting
    await _app.col_settings.update_one(
        {"key": "autodelete_minutes"},
        {"$setOnInsert": {"value": Config.AUTO_DELETE_MINUTES_DEFAULT}},
        upsert=True
    )
    log.info("Bot started.")

@app.on_stop()
async def _on_stop(_app: Client):
    try:
        _app.mongo.close()
    except Exception:
        pass
    log.info("Bot stopped.")

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass
    app.run()
