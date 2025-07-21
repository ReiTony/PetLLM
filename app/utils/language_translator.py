import asyncio
import logging
from langdetect import detect
from googletrans import Translator

logger = logging.getLogger("translation")
translator = Translator()

ALLOWED_LANGUAGES = {"en", "ko", "ja", "tl"}  # English, Korean, Japanese, Filipino

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        if lang in ALLOWED_LANGUAGES:
            return lang
        else:
            logger.warning(f"Detected unsupported language '{lang}', defaulting to 'en'.")
            return "en"
    except Exception as e:
        logger.error(f"[LangDetect Error]: {e}")
        return "en"

def translate_to_eng(text: str, src_lang: str) -> str:
    if src_lang == "en":
        return text
    try:
        translated = translator.translate(text, src=src_lang, dest="en")
        logger.info(f"[Translate → EN] ({src_lang}): {text} → {translated.text}")
        return translated.text
    except Exception as e:
        logger.error(f"[Translation to EN Error]: {e}")
        return text

def translate_to_user_lang(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    try:
        translated = translator.translate(text, dest=target_lang)
        logger.info(f"[Translate → {target_lang.upper()}]: {text} → {translated.text}")
        return translated.text
    except Exception as e:
        logger.error(f"[Translation to User Lang Error]: {e}")
        return text

async def translate_to_english(text: str, src_lang: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, translate_to_eng, text, src_lang)

async def translate_to_user_language(text: str, target_lang: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, translate_to_user_lang, text, target_lang)
