import os
import sys
import random
from datetime import datetime
from dotenv import load_dotenv

from config import YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID, DRY_RUN
from googleapiclient.discovery import build

from storage.db import DB
from ai.generator import generate_hero_post
from publisher.telegram_client import send_post
from heroes_list import HEROES  # список всех 126 героев

load_dotenv()

# Добавляем путь для корректного импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pick_new_hero(db: DB) -> str:
    """Выбираем случайного героя, которого ещё не постили"""
    used = db.used_heroes()
    remaining = [h for h in HEROES if h not in used]

    if not remaining:
        print("Все герои уже использованы! 🎉 Сбрасываем прогресс.")
        db.reset_heroes()
        remaining = HEROES[:]

    return random.choice(remaining)


def find_hero_video(youtube, hero_name: str) -> tuple[str, str, str] | None:
    """Ищем видео на YouTube по имени героя"""
    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        q=hero_name,
        order="relevance",
        maxResults=1
    )
    response = request.execute()
    items = response.get("items", [])

    for item in items:
        if item["id"]["kind"] != "youtube#video":
            continue
        video_id = item["id"]["videoId"]
        video_title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_title, video_url, item["snippet"]["publishedAt"]

    return None


def run_hero_post():
    db = DB()
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    hero = pick_new_hero(db)
    print(f"🎯 Выбран герой: {hero}")

    video_data = find_hero_video(youtube, hero)
    if not video_data:
        print(f"⚠️ Видео по герою {hero} не найдено")
        return

    video_title, video_url, published_at = video_data

    # Проверяем — публиковалось ли это видео
    if db.seen(f"hero:{hero}"):
        print(f"Герой {hero} уже был опубликован")
        return

    # Генерируем пост через AI
    post_text = generate_hero_post(hero=hero, video_url=video_url)

    if DRY_RUN:
        print("=== TEST POST ===")
        print(post_text)
        print("=================")
        return

    success = send_post(post_text)
    if success:
        db.add_if_absent(f"hero:{hero}", hero, "HeroTrick", published_at)
        db.mark_posted(f"hero:{hero}")
        print(f"✅ Опубликован пост с героем {hero}")


if __name__ == "__main__":
    print("=== Running MLBB Hero Trick Bot ===")
    run_hero_post()
    print("=== Run finished ===")
