from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGO_URI = config("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.petpal_db  # matches your screenshot

# Expose the chats collection directly
chats_collection = db.chats

def get_db():
    return db
