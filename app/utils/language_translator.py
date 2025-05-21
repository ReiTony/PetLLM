from langdetect import detect
from googletrans import Translator

translator = Translator()

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception as e:
        print(f"[LangDetect Error]: {e}")
        return "en"  


def translate_to_english(text: str, src_lang: str) -> str:
    if src_lang == "en":
        return text
    try:
        translated = translator.translate(text, src=src_lang, dest="en")
        print(f"[Translate → EN] ({src_lang}): {text} → {translated.text}")
        return translated.text
    except Exception as e:
        print(f"[Translation to EN Error]: {e}")
        return text


def translate_to_user_language(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    try:
        translated = translator.translate(text, dest=target_lang)
        print(f"[Translate → {target_lang.upper()}]: {text} → {translated.text}")
        return translated.text
    except Exception as e:
        print(f"[Translation to User Lang Error]: {e}")
        return text
