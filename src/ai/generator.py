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
    if not OPENROUTER_API_KEY:
        # Fallback если API-ключа нет
        return f"{hero} trick is waiting for you! 🔥\nCheck the video 👇\n{video_url}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "temperature": 0.9,  # больше креативности
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(hero=hero)},
        ],
    }

    try:
        r = requests.post(OPENROUTER_URL, json=payload,
                          headers=headers, timeout=40)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"].strip()

        # добавляем ссылку в конце
        if video_url not in content:
            content += f"\n{video_url}"

        return content

    except Exception as e:
        # fallback
        return f"{hero} trick is waiting for you! 🔥\nCheck the video 👇\n{video_url}"
