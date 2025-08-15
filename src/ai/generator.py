import os
import requests
from typing import Optional
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, LANGUAGE


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a social media editor for a Mobile Legends: Bang Bang Telegram channel. "
    "Write concise, enthusiastic, and factual posts in English. Never invent facts."
)

USER_TEMPLATE = (
    "Rewrite the following news into a short Telegram post in English. "
    "Constraints: 2-4 short sentences, no more than 220 words total. "
    "Use 1-3 fitting emojis and 2-5 relevant hashtags at the end. "
    "Keep it factual; do not add release dates or details not present in the input.\n\n"
    "Title: {title}\n"
    "Link: {url}\n"
    "Optional summary: {summary}"
)


def generate_post(title: str, url: str, summary: Optional[str] = None) -> str:
    if not OPENROUTER_API_KEY:
        # Fallback без ИИ — безопасно и полезно для отладки
        base = f"{title}\n\n{url}"
        return base

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(
                title=title, url=url, summary=summary or "")},
        ],
    }
    try:
        r = requests.post(OPENROUTER_URL, json=payload,
                          headers=headers, timeout=40)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"].strip()
        # На всякий случай добавим ссылку в конце
        if url not in content:
            content += f"\n\n{url}"
        return content
    except Exception as e:
        # Не ломаем весь пайплайн, возвращаем fallback
        return f"{title}\n\n{url}"
