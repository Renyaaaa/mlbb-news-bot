import os
import requests
import random
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, client, LANGUAGE

# Конфигурация для разных провайдеров
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

SYSTEM_PROMPT = (
    "You are a Mobile Legends: Bang Bang content creator for a Telegram channel. "
    "Your task is to write short, hype, and engaging posts in English about tricks or tips or tutorial with specific heroes. "
    "Keep it fun, natural, and like social media captions. Avoid long explanations."
)

USER_TEMPLATE = (
    "Create a completely unique and specific post about the hero {hero} from Mobile Legends: Bang Bang. "
    "Focus on their unique abilities, playstyle, or specific mechanics that make them special. "
    "Mention a specific trick, combo, or strategy that is unique to this hero. "
    "Make it sound exciting and different from any other hero post. "
    "Constraints: 1-2 sentences, max 60 words. "
    "Style: unique, hype, and specific to this hero. "
    "End with 'Check the video 👇'. "
    "Do not use generic phrases like 'unleash power' or 'master the art'. "
    "Be specific about what makes {hero} unique."
)

# Fallback шаблоны для генерации постов
FALLBACK_TEMPLATES = [
    "🔥 {hero} is waiting to dominate the battlefield! Master their ultimate combo and become unstoppable! Check the video 👇",
    "⚡ Want to carry your team with {hero}? This tutorial reveals the secret strategies that pros use! Check the video 👇",
    "🎯 {hero} can be your ticket to Mythic rank! Learn the positioning and timing that makes all the difference! Check the video 👇",
    "💎 Discover why {hero} is secretly OP! This guide shows you the build and playstyle that wins games! Check the video 👇",
    "🚀 Ready to unlock {hero}'s true potential? This tutorial teaches you the advanced mechanics that separate good from great! Check the video 👇",
    "⚔️ {hero} dominates the front line! Master the balance of damage and survivability to carry your team! Check the video 👇",
    "🎮 {hero} is the hero you've been waiting for! Learn their unique playstyle and dominate every match! Check the video 👇",
    "🌟 {hero} can turn any game around! Master their skills and become the MVP your team needs! Check the video 👇",
    "💪 {hero} is your path to victory! This tutorial reveals the strategies that make them unstoppable! Check the video 👇",
    "🎲 {hero} is the wildcard that wins games! Learn their unpredictable playstyle and surprise your enemies! Check the video 👇",
    "🔥 Master {hero}'s signature combo and watch enemies fall! This guide reveals the timing that makes all the difference! Check the video 👇",
    "⚡ {hero} isn't just strong - they're strategically brilliant! Learn the positioning that makes them unstoppable! Check the video 👇",
    "🎯 Every {hero} player needs to know this! Master their unique mechanics and dominate the battlefield! Check the video 👇",
    "💎 {hero} has a secret that most players miss! Discover the build and strategy that wins games! Check the video 👇",
    "🚀 Ready to master {hero}? This tutorial shows you the advanced techniques that separate pros from amateurs! Check the video 👇"
]

# Персонализированные посты для конкретных героев
HERO_SPECIFIC_POSTS = {
    "Layla": [
        "🎯 {hero} is the ultimate late-game carry! Master farming and positioning to become unstoppable! Check the video 👇",
        "💥 {hero} can 1v5 the entire enemy team! Learn the positioning that makes her a nightmare! Check the video 👇",
        "🎯 {hero}'s range is her weapon! Master the distance and watch enemies fall before they can reach you! Check the video 👇"
    ],
    "Claude": [
        "⚡ {hero} is the fastest marksman alive! Master his mobility and kite enemies to death! Check the video 👇",
        "🎭 {hero} is the trickster of the battlefield! Learn his unique mechanics and outplay everyone! Check the video 👇",
        "⚡ {hero}'s dash is everything! Master the timing and positioning to become untouchable! Check the video 👇"
    ],
    "Hanabi": [
        "🌸 {hero} blooms in team fights! Master her ultimate timing and watch enemies fall like petals! Check the video 👇",
        "💫 {hero} is the queen of positioning! Learn how to stay safe while dealing massive damage! Check the video 👇",
        "🌸 {hero}'s ultimate can change the entire game! Master the timing and watch your team dominate! Check the video 👇"
    ],
    "Balmond": [
        "🪓 {hero} is the executioner! Master his ultimate timing and secure every kill! Check the video 👇",
        "💀 {hero} brings death to the battlefield! Learn his aggressive playstyle and dominate! Check the video 👇",
        "🪓 {hero}'s spin is his signature move! Master the timing and watch enemies fall! Check the video 👇"
    ],
    "Uranus": [
        "🛡️ {hero} is the unbreakable shield! Master his defensive mechanics and protect your team! Check the video 👇",
        "🌌 {hero} controls the battlefield! Learn his zoning abilities and control every fight! Check the video 👇",
        "🛡️ {hero} is the ultimate protector! Master his taunt timing and save your carries! Check the video 👇"
    ],
    "Minsitthar": [
        "⚔️ {hero} is the battlefield commander! Master his ultimate timing and control every team fight! Check the video 👇",
        "🛡️ {hero} leads from the front! Learn his initiation and watch your team dominate! Check the video 👇",
        "⚔️ {hero}'s ultimate is game-changing! Master the positioning and secure every objective! Check the video 👇"
    ],
    "Akai": [
        "🐼 {hero} is the ultimate disruptor! Master his ultimate timing and scatter enemy formations! Check the video 👇",
        "🛡️ {hero} controls the battlefield! Learn his positioning and protect your carries! Check the video 👇",
        "🐼 {hero}'s ultimate can win team fights! Master the timing and watch enemies panic! Check the video 👇"
    ],
    "Dyrroth": [
        "🔥 {hero} is the beast of the battlefield! Master his ultimate timing and dominate every fight! Check the video 👇",
        "⚔️ {hero} brings raw power! Learn his combo timing and watch enemies fall! Check the video 👇",
        "🔥 {hero}'s ultimate is devastating! Master the positioning and secure every kill! Check the video 👇"
    ]
}


def generate_with_anthropic(hero: str) -> str:
    """Генерация через Anthropic Claude"""
    if not ANTHROPIC_API_KEY:
        return None

    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 150,
            "messages": [
                {"role": "user", "content": USER_TEMPLATE.format(hero=hero)}
            ]
        }

        response = requests.post(
            ANTHROPIC_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        content = result["content"][0]["text"].strip()
        print(f"✅ Anthropic Claude сгенерировал: {content}")
        return content

    except Exception as e:
        print(f"⚠️ Ошибка Anthropic: {e}")
        return None


def generate_with_gemini(hero: str) -> str:
    """Генерация через Google Gemini"""
    if not GEMINI_API_KEY:
        return None

    try:
        url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"

        data = {
            "contents": [{
                "parts": [{
                    "text": USER_TEMPLATE.format(hero=hero)
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 150,
                "temperature": 0.8
            }
        }

        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"✅ Google Gemini сгенерировал: {content}")
        return content

    except Exception as e:
        print(f"⚠️ Ошибка Gemini: {e}")
        return None


def generate_with_openrouter(hero: str) -> str:
    """Генерация через OpenRouter"""
    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_TEMPLATE.format(hero=hero)}
            ],
            max_tokens=150,
            temperature=0.8
        )

        content = response.choices[0].message.content.strip()
        print(f"✅ OpenRouter сгенерировал: {content}")
        return content

    except Exception as e:
        print(f"⚠️ Ошибка OpenRouter: {e}")
        return None


def clean_text_for_telegram(text: str, max_length: int = 1000) -> str:
    """
    Очищает текст для отправки в Telegram
    """
    # Убираем лишние пробелы и переносы строк
    cleaned = " ".join(text.split())

    # Ограничиваем длину
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length-3] + "..."

    return cleaned


def generate_hero_post(hero: str, video_url: str) -> str:
    """
    Генерирует короткий пост для героя с YouTube ссылкой.
    Пробует разные ИИ провайдеры в порядке приоритета.
    """
    print(f"🤖 Генерирую пост для героя {hero}...")

    # Пробуем разные ИИ провайдеры в порядке приоритета
    ai_providers = [
        ("OpenRouter", lambda: generate_with_openrouter(hero)),
        ("Anthropic Claude", lambda: generate_with_anthropic(hero)),
        ("Google Gemini", lambda: generate_with_gemini(hero))
    ]

    for provider_name, provider_func in ai_providers:
        print(f"  🔄 Пробуем {provider_name}...")
        try:
            content = provider_func()
            if content:
                # Добавляем ссылку на видео, если её нет
                if video_url not in content:
                    content += f"\n\n{video_url}"

                # Очищаем текст для Telegram
                content = clean_text_for_telegram(content)
                return content
        except Exception as e:
            print(f"    ⚠️ {provider_name} недоступен: {e}")
            continue

    # Если все ИИ недоступны, используем улучшенный fallback
    print("  🔄 Все ИИ недоступны, использую fallback...")

    # Проверяем, есть ли персонализированные посты для героя
    if hero in HERO_SPECIFIC_POSTS:
        fallback_template = random.choice(HERO_SPECIFIC_POSTS[hero])
        print(f"  🎯 Использую персонализированный шаблон для {hero}")
    else:
        fallback_template = random.choice(FALLBACK_TEMPLATES)
        print(f"  🎲 Использую общий шаблон для {hero}")

    fallback_text = fallback_template.format(hero=hero)
    fallback_text += f"\n\n{video_url}"

    # Очищаем fallback текст тоже
    fallback_text = clean_text_for_telegram(fallback_text)

    print(f"✅ Fallback генератор создал: {fallback_text}")
    return fallback_text


def generate_hero_post_alternative(hero: str, video_url: str) -> str:
    """
    Альтернативный генератор постов без внешних API
    """
    print(f"🤖 Генерирую альтернативный пост для героя {hero}...")

    # Создаем персонализированный пост на основе имени героя
    hero_traits = {
        "Layla": "marksman", "Claude": "marksman", "Hanabi": "marksman",
        "Tank": "tank", "Support": "support", "Mage": "mage",
        "Fighter": "fighter", "Assassin": "assassin"
    }

    # Определяем роль героя (упрощенно)
    role = "hero"
    for trait, hero_role in hero_traits.items():
        if trait.lower() in hero.lower():
            role = hero_role
            break

    # Генерируем пост на основе роли
    role_posts = {
        "marksman": f"🎯 {hero} is the ultimate carry! Master positioning and farming to dominate late game! Check the video 👇",
        "tank": f"🛡️ {hero} leads the charge! Learn proper initiation and team fight positioning! Check the video 👇",
        "support": f"💙 {hero} keeps the team alive! Master timing and positioning for maximum impact! Check the video 👇",
        "mage": f"✨ {hero} controls the battlefield! Learn combo timing and skill rotations! Check the video 👇",
        "fighter": f"⚔️ {hero} dominates the front line! Master the balance of damage and survivability! Check the video 👇",
        "assassin": f"🗡️ {hero} strikes from the shadows! Learn proper timing and target selection! Check the video 👇",
        "hero": f"🔥 {hero} is ready to carry your team! Master their unique mechanics and become unstoppable! Check the video 👇"
    }

    post = role_posts.get(role, role_posts["hero"])
    post += f"\n\n{video_url}"

    print(f"✅ Альтернативный генератор создал: {post}")
    return post
