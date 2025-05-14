from fastapi import APIRouter, HTTPException, Depends
from app.models.main_schema import get_user_profile_form
from app.db.connection import get_db

router = APIRouter()
db = get_db()

@router.post("/user-profile")
async def create_user_profile(profile: dict = Depends(get_user_profile_form)):
    print("🔍 Incoming profile:", profile)

    await db.users.update_one(
        {"user_id": profile["user_id"]},
        {"$set": profile},
        upsert=True
    )
    return {"message": "User profile saved successfully"}
