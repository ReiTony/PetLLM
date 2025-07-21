from app.utils.chat_handler import generate_response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def is_teachable_fact(message: str) -> bool:
    prompt = (
        "You are a strict AI knowledge classifier. "
        "Decide if the following user message is a clear factual statement or personal information a pet should remember. "
        "ONLY answer with YES or NO. Do NOT explain.\n"
        "Here are examples (answer YES or NO):\n"
        "- My name is Jake. → YES\n"
        "- I am a teacher. → YES\n"
        "- Banana is a fruit. → YES\n"
        "- My favorite color is red. → YES\n"
        "- We go for walks every morning. → YES\n"
        "- My birthday is in April. → YES\n"
        "- Red is the color of apples. → YES\n"
        "- I love pizza. → YES\n"
        "- I am Jake and I like pizza. → YES\n"
        "- The sky is blue. → YES\n"
        "- Let's go for a walk! → NO\n"
        "- Can you hear me? → NO\n"
        "- I'm feeling tired. → NO\n"
        "- Let's play fetch! → NO\n"
        "- Sit! → NO\n"
        "- What are you doing? → NO\n"
        "- Do you want to go outside? → NO\n"
        "\nUser message:\n"
        f"{message}\n"
        "Answer (YES or NO only):"
    )
    try:
        result = await generate_response(prompt, use_mock=False)
        logger.info(f"[Fact Check] LLM replied: {result.strip()}")
        return result.strip().lower().startswith("yes")
    except Exception as e:
        logger.warning(f"[Fact Detection Error]: {e}")
        return False
