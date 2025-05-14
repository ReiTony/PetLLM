from fastapi import APIRouter, Depends, HTTPException
from app.models.main_schema import get_pet_profile_form
from app.db.connection import get_db

router = APIRouter()
db = get_db()

@router.post("/pet-profile")
async def create_pet_profile(pet_data: dict = Depends(get_pet_profile_form)):
    print("Incoming pet profile:", pet_data)

    user = await db.users.find_one({"user_id": pet_data["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User ID not found. Please register user first.")

    await db.pets.update_one(
        {"user_id": pet_data["user_id"]},
        {"$set": pet_data},
        upsert=True
    )
    return {"message": "Pet profile saved successfully"}
