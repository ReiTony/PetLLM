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

    # --- DATA FETCH ---
    try:
        user_data = await get_user_by_id(user_id, authorization)
        if not user_data or "first_name" not in user_data:
            raise ValueError("Missing owner_name in user profile.")
    except Exception as e:
        logger.error("User fetch error: %s", e)
        raise HTTPException(status_code=500, detail="Error retrieving user data.")

    try:
        pet_data = await get_pet_by_id(pet_id, authorization)
        if not pet_data:
            raise ValueError("Pet profile not found.")
    except Exception as e:
        logger.error("Pet fetch error: %s", e)
        raise HTTPException(status_code=500, detail="Error retrieving pet data.")

    try:
        pet_status_data = await get_pet_status_by_id(pet_id, authorization)
    except Exception as e:
        logger.error("Pet status fetch error: %s", e)
        raise HTTPException(status_code=500, detail="Error retrieving pet status.")

    owner_name = user_data["first_name"]
    logger.info("✔ User Profile — Name: %s", owner_name)
    logger.info("✔ Pet Profile — Species: %s | Breed: %s | Name: %s", pet_data.get("species"), pet_data.get("breed"), pet_data.get("name"))

    # --- LANGUAGE DETECTION ---
    user_lang = detect_language(message)
    logger.info("Detected user language: %s", user_lang)
    translated_message = translate_to_english(message, user_lang)
    if translated_message != message:
        logger.info("Translated message to English: %s", translated_message)

    # --- SHORT-TERM MEMORY ---
    recent_chats_cursor = chats_collection.find({
        "user_id": user_id,
        "pet_id": pet_id
    }).sort("timestamp", -1).limit(5)

    recent_chats = await recent_chats_cursor.to_list(length=5)

    def truncate_text(text: str, max_chars=250):
        return text[:max_chars].rsplit(" ", 1)[0] + "..." if len(text) > max_chars else text

    memory_snippet = "\n".join(
        f"User: {truncate_text(chat['user_message'])}\nPet: {truncate_text(chat['pet_response'])}"
        for chat in reversed(recent_chats)
    )

    if memory_snippet:
        logger.info("\n===== MEMORY SNIPPET START =====\n%s\n===== MEMORY SNIPPET END =====", memory_snippet)
    else:
        logger.info("ℹ No recent memory found for user/pet.")

    # --- PROMPT GENERATION ---
    prompt = build_pet_prompt(pet_data, owner_name, memory_snippet=memory_snippet, pet_status=pet_status_data)
    prompt += f"\n\nUser: {translated_message}\n{pet_data.get('species', 'pet').capitalize()}:"
    logger.info("\n--- Prompt Sent to LLM ---\n%s", prompt)

    # --- LLM RESPONSE ---
    response = await generate_response(prompt, use_mock=False)
    if response.startswith("[ERROR]"):
        logger.warning("Model returned error: %s", response)
        raise HTTPException(status_code=502, detail="AI response unavailable")

    logger.info("Model Response (EN):\n%s", response.strip())
    translated_response = translate_to_user_language(response.strip(), user_lang)
    if translated_response != response.strip():
        logger.info("Translated response to %s: %s", user_lang, translated_response)

    # --- STORE CHAT ---
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
