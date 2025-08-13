from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

try:
    MONGO_URI = config("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI is empty")
except Exception as exc:
    logger.error("MONGO_URI configuration error: %s", exc)
    raise RuntimeError("MONGO_URI not configured") from exc

@lru_cache(maxsize=1)
def get_client() -> AsyncIOMotorClient:
    # One client per process; reused across calls
    return AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)

@lru_cache(maxsize=1)
def get_db():
    return get_client().petpal_db

# Expose the collections directly (unchanged usage)
db = get_db()
chats_collection = db.chats
user_profiles_collection = db.user_profiles
