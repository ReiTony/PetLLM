import httpx
from httpx import HTTPError
from better_profanity import profanity
from decouple import config

OPENAI_API_KEY = config("OPENAI_API_KEY")
profanity.load_censor_words()

async def is_flagged_content(text: str) -> bool:
    # 1. Local check (fast and free)
    if profanity.contains_profanity(text):
        print("[Moderation] Local profanity detected")
        return True

    # 2. OpenAI Moderation API check
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/moderations",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"input": text}
            )
            response.raise_for_status()
            result = response.json()
            flagged = result["results"][0]["flagged"]

            if flagged:
                print("[Moderation] OpenAI flagged the input")
            return flagged

    except HTTPError as e:
        if e.response.status_code == 429:
            print("[Moderation Warning] Rate limit hit. Using local check only.")
        else:
            print(f"[Moderation Error]: {e.response.status_code} - {e.response.text}")
        return False

    except Exception as e:
        print(f"[Moderation Unexpected Error]: {e}")
        return False
