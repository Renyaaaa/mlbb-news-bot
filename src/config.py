import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL", "")

# YouTube
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

# Проверка
if not YOUTUBE_API_KEY or not YOUTUBE_CHANNEL_ID:
    print("Warning: YouTube variables are missing!")


# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")


POST_LIMIT_PER_RUN = int(os.getenv("POST_LIMIT_PER_RUN", "2"))
LANGUAGE = os.getenv("LANGUAGE", "en")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# базовые проверки при старте
REQUIRED = {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHANNEL": TELEGRAM_CHANNEL,
    "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
}
for k, v in REQUIRED.items():
    if not v:
        raise RuntimeError(f"Missing required env var: {k}")

# инициализация клиента OpenRouter

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",  # важно указать base_url
    api_key=OPENROUTER_API_KEY
)

# Пример функции генерации поста


def generate_post(news_text):
    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {"role": "system", "content": f"You are a news writer for a Mobile Legends Telegram channel. Write short, catchy posts in {LANGUAGE} with emojis and hashtags."},
            {"role": "user", "content": news_text}
        ]
    )
    return response.choices[0].message.content
