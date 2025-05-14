from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGO_URI = config("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.petpal_db

def get_db():
    """
    Returns the database connection.
    """
    return db