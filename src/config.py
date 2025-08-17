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

# Anthropic Claude
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

POST_LIMIT_PER_RUN = int(os.getenv("POST_LIMIT_PER_RUN", "2"))
LANGUAGE = os.getenv("LANGUAGE", "en")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# базовые проверки при старте
REQUIRED = {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHANNEL": TELEGRAM_CHANNEL,
}

# Проверяем, что хотя бы один ИИ провайдер доступен
AI_PROVIDERS = {
    "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    "GEMINI_API_KEY": GEMINI_API_KEY,
}

ai_available = any(AI_PROVIDERS.values())
if not ai_available:
    print("⚠️ Warning: No AI provider API keys found!")
    print("   The bot will use fallback text generation")

for k, v in REQUIRED.items():
    if not v:
        raise RuntimeError(f"Missing required env var: {k}")

# инициализация клиента OpenRouter (если доступен)
client = None
if OPENROUTER_API_KEY:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",  # важно указать base_url
            api_key=OPENROUTER_API_KEY
        )
        print("✅ OpenRouter client initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize OpenRouter client: {e}")
else:
    print("ℹ️ OpenRouter not configured")
