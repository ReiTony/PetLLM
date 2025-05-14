from fastapi import APIRouter, Depends
from app.models.main_schema import get_chat_form
from app.db.connection import get_db
from app.utils.prompt_builder import build_pet_prompt
from app.utils.chat_handler import generate_response

router = APIRouter()
db = get_db()

@router.post("/chat")
async def chat(form: dict = Depends(get_chat_form)):
    user_data = await db.users.find_one({ "user_id": form["user_id"] })
    pet_data = await db.pets.find_one({ "user_id": form["user_id"] })

    if not user_data or not pet_data:
        return { "error": "User or pet profile not found." }

    pet_type = pet_data.get("pet_type", "Pet").capitalize()
    prompt = build_pet_prompt(pet_data, user_data["mbti"]) + f"\n\nUser: {form['message']}\n{pet_type}:"
    response = generate_response(prompt, use_mock=False)
    final_reply = response.strip()

    await db.chats.insert_one({
        "user_id": form["user_id"],
        "pet_type": pet_type.lower(),
        "user_message": form["message"],
        "bot_response": final_reply,
    })

    return { "response": final_reply }
