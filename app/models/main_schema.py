from pydantic import BaseModel
from fastapi import Form
from typing import Literal

# User Profile Form
def get_user_profile_form(
    user_id: str = Form(...),
    age: int = Form(...),
    mbti: Literal["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
                  "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"] = Form(...)
):
    return {
        "user_id": user_id,
        "age": age,
        "mbti": mbti
    }

# Pet Profile Form 
def get_pet_profile_form(
    user_id: str = Form(...),
    pet_name: str = Form(...),
    pet_type: Literal["cat", "dog"] = Form(...),
    breed: Literal[
        "Golden Retriever", "Shiba Inu", "Husky",  # Dogs
        "Persian", "Siamese", "Bengal"             # Cats
    ] = Form(...),
    pet_age_group: Literal["baby", "teen", "adult"] = Form(...)
):
    return {
        "user_id": user_id,
        "pet_name": pet_name,
        "pet_type": pet_type,
        "breed": breed,
        "age_group": pet_age_group
    }

# Chat Request 
def get_chat_form(
    user_id: str = Form(...),
    message: str = Form(...)
):
    return {
        "user_id": user_id,
        "message": message
    }
