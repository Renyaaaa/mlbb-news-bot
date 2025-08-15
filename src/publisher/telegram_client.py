import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL, DRY_RUN

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_post(text: str):
    if DRY_RUN:
        print("[DRY_RUN] Post would be sent:")
        print(text)
        return True

    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(f"{BASE_URL}/sendMessage", data=payload, timeout=20)
        r.raise_for_status()
        return True
    except Exception as e:
        print("Failed to send Telegram post:", e)
        return False
