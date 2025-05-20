import logging
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header

from app.models.main_schema import get_chat_form, ChatResponse
from app.utils.prompt_builder import build_pet_prompt
from app.utils.chat_handler import generate_response
from app.utils.php_service import get_user_by_id, get_pet_by_id
from app.utils.extract_response import extract_response_features
from app.db.connection import chats_collection

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_auth_token(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return authorization


@router.post("/chat", response_model=ChatResponse)
async def chat(
    form: dict = Depends(get_chat_form), authorization: str = Depends(get_auth_token)
):
    user_id = form.get("user_id")
    pet_id = form.get("pet_id")
    message = form.get("message")

    logger.info("Received chat request for user_id: %s, pet_id: %s", user_id, pet_id)

    try:
        user_data, pet_data = await asyncio.gather(
            get_user_by_id(user_id, authorization), get_pet_by_id(pet_id, authorization)
        )
    except Exception as e:
        logger.error("Failed to retrieve user or pet data: %s", str(e))
        raise HTTPException(
            status_code=500, detail="Failed to retrieve user/pet profile."
        )

    if not user_data or "mbti" not in user_data or "first_name" not in user_data:
        raise HTTPException(
            status_code=422, detail="User profile missing MBTI or first name."
        )
    if not pet_data:
        raise HTTPException(status_code=404, detail="Pet profile not found.")

    mbti = user_data["mbti"]
    owner_name = user_data["first_name"]

    logger.info("MBTI: %s | Owner: %s", mbti, owner_name)
    logger.info("Pet data: %s", pet_data)

    prompt = build_pet_prompt(pet_data, mbti, owner_name)
    prompt += f"\n\nUser: {message}\n{pet_data.get('species', 'pet').capitalize()}:"
    logger.debug("Prompt sent to model:\n%s", prompt)

    response = await generate_response(prompt, use_mock=False)

    if response.startswith("[ERROR]"):
        logger.warning("Model returned error: %s", response)
        raise HTTPException(status_code=502, detail="AI response unavailable")

    logger.info("Model response: %s", response.strip())
    features = extract_response_features(response)

    await chats_collection.insert_one(
        {
            "user_id": user_id,
            "pet_id": pet_id,
            "timestamp": datetime.utcnow(),
            "user_message": message,
            "pet_response": response.strip(),
        }
    )

    return {"response": response.strip(), "features": features}
