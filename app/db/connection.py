from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
import logging

logger = logging.getLogger(__name__)

try:
    MONGO_URI = config("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI is empty")
except Exception as exc:
    logger.error("MONGO_URI configuration error: %s", exc)
    raise RuntimeError("MONGO_URI not configured") from exc

client = AsyncIOMotorClient(MONGO_URI)
db = client.petpal_db  

chats_collection = db.chats

def get_db():
    return db