import logging
import asyncio
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header

from app.models.main_schema import get_chat_form, ChatResponse
from app.utils.prompt_builder import build_pet_prompt
from app.utils.chat_handler import generate_response
from app.utils.php_service import get_user_by_id, get_pet_by_id, get_pet_status_by_id
from app.utils.extract_response import extract_response_features
from app.db.connection import chats_collection
from app.utils.language_translator import (
    detect_language,
    translate_to_english,
    translate_to_user_language
)
# from ip_features.content_moderator import is_flagged_content  # ⛔ disabled for testing

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Soft warning responses (unused for now since moderation is disabled)
SOFT_WARNINGS = [
    "(confused) {tilt head} <whimper>\nHmm? That didn’t sound right. Let's talk about something fun!",
    "(anxious) {crouch down} <whimper>\nUmm... I don’t think I understand that. Can we talk about something else?",
    "(confused) {perk ears} <sniff sniff>\nThat feels weird. Maybe try saying it differently?",
    "(sleepy) {lie down} <yawn>\nThat’s a bit too strange for me. Let’s cuddle instead.",
    "(anxious) {sit beside} <whimper>\nI'm not sure I like that. Can we change the topic?",
    "(sad) {bow head} <whimper>\nThat makes me feel icky. Want to play instead?"
]


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

    logger.info("\n--- Chat Request Received ---\nUser ID: %s | Pet ID: %s", user_id, pet_id)

    try:
        user_data, pet_data, pet_status_data = await asyncio.gather(
            get_user_by_id(user_id, authorization),
            get_pet_by_id(pet_id, authorization),
            get_pet_status_by_id(pet_id, authorization)
        )
    except Exception as e:
        logger.error("Failed to retrieve user or pet data: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve user/pet profile.")

    if not user_data or "mbti" not in user_data or "first_name" not in user_data:
        raise HTTPException(status_code=422, detail="User profile missing MBTI or first name.")
    if not pet_data:
        raise HTTPException(status_code=404, detail="Pet profile not found.")

    mbti = user_data["mbti"]
    owner_name = user_data["first_name"]

    logger.info("✔ User Profile — MBTI: %s | Name: %s", mbti, owner_name)
    logger.info("✔ Pet Profile — Species: %s | Breed: %s | Name: %s", pet_data.get("species"), pet_data.get("breed"), pet_data.get("name"))

    # Step 1: Detect user language
    user_lang = detect_language(message)
    logger.info("Detected user language: %s", user_lang)

    # Step 2: Translate to English if necessary
    translated_message = translate_to_english(message, user_lang)
    if translated_message != message:
        logger.info("Translated message to English: %s", translated_message)

    # Step 3: ⛔ Content moderation is temporarily disabled
    # if await is_flagged_content(translated_message):
    #     logger.warning("[MODERATION] User input flagged by content filter.")
    #     soft_warning = random.choice(SOFT_WARNINGS)
    #     await chats_collection.insert_one({
    #         "user_id": user_id,
    #         "pet_id": pet_id,
    #         "timestamp": datetime.utcnow(),
    #         "user_message": message,
    #         "pet_response": soft_warning,
    #         "flagged": True
    #     })
    #     return {
    #         "response": soft_warning,
    #         "features": extract_response_features(soft_warning)
    #     }

    # Step 4: Short-term memory
    recent_chats_cursor = chats_collection.find({
        "user_id": user_id,
        "pet_id": pet_id
    }).sort("timestamp", -1).limit(5)

    recent_chats = await recent_chats_cursor.to_list(length=5)

    if recent_chats:
        formatted_chats = "\n\n".join(
            f"[{i}] User: {chat['user_message']}\n    Pet: {chat['pet_response']}"
            for i, chat in enumerate(reversed(recent_chats), 1)
        )
        logger.info("\n===== MEMORY SNIPPET START =====\n%s\n===== MEMORY SNIPPET END =====", formatted_chats)
    else:
        logger.info("ℹ No recent memory found for user/pet.")

    memory_snippet = "\n".join(
        f"User: {chat['user_message']}\nPet: {chat['pet_response']}"
        for chat in reversed(recent_chats)
    )

    # Step 5: Build prompt
    prompt = build_pet_prompt(pet_data, mbti, owner_name, memory_snippet=memory_snippet, pet_status=pet_status_data)
    prompt += f"\n\nUser: {translated_message}\n{pet_data.get('species', 'pet').capitalize()}:"

    logger.info("\n--- Prompt Sent to LLM ---\n%s", prompt)

    # Step 6: Generate response
    response = await generate_response(prompt, use_mock=False)

    if response.startswith("[ERROR]"):
        logger.warning("Model returned error: %s", response)
        raise HTTPException(status_code=502, detail="AI response unavailable")

    logger.info("Model Response (EN):\n%s", response.strip())

    # Step 7: Translate response back to user language if needed
    translated_response = translate_to_user_language(response.strip(), user_lang)
    if translated_response != response.strip():
        logger.info("Translated response to %s: %s", user_lang, translated_response)

    # Step 8: Store chat and return
    features = extract_response_features(response)

    await chats_collection.insert_one({
        "user_id": user_id,
        "pet_id": pet_id,
        "timestamp": datetime.utcnow(),
        "user_message": message,
        "pet_response": translated_response
    })

    logger.info("Chat successfully stored in MongoDB")

    return {"response": translated_response, "features": features}
