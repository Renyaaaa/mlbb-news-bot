import os
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a Mobile Legends: Bang Bang content creator for a Telegram channel. "
    "Your task is to write short, hype, and engaging posts in English about tricks or tips or tutorial with specific heroes. "
    "Keep it fun, natural, and like social media captions. Avoid long explanations."
)

USER_TEMPLATE = (
    "Create a unique short post about the hero {hero} from Mobile Legends: Bang Bang. "
    "Constraints: 1–2 short sentences, max 50 words. "
    "Style: catchy, hype, and mysterious. "
    "Mention a trick or tip or tutorial (without too much detail). "
    "End with a call to action like 'Check the video 👇'. "
    "Do not invent abilities that don't exist. "
    "Do not include hashtags."
)


def generate_hero_post(hero: str, video_url: str) -> str:
    """
    Генерирует короткий пост для героя с YouTube ссылкой.
    """
    SYSTEM_PROMPT = f"You are a news writer for a Mobile Legends Telegram channel. Write short, catchy posts in {LANGUAGE} with emojis and hashtags."
    USER_TEMPLATE = f"Create a short, engaging post for the hero {hero}.\nInclude a call to watch the video:"

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_TEMPLATE}
            ]
        )
        # новый синтаксис SDK
        content = response.choices[0].message['content'].strip()
        if video_url not in content:
            content += f"\n{video_url}"
        return content
    except Exception as e:
        print("⚠️ OpenRouter error:", e)
        # fallback текст
        return f"{hero} tutorial is waiting for you! 🔥\nCheck the video 👇\n{video_url}"
