from config import YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID
from googleapiclient.discovery import build
from config import DRY_RUN
from storage.db import DB
from ai.generator import generate_post
from publisher.telegram_client import send_post
from sources.ml_official import MLOfficialNews
from sources.gamerbraves import GamerBravesML
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Добавляем путь для корректного импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SOURCES = [MLOfficialNews(), GamerBravesML()]


def run_news():
    db = DB()

    for source in SOURCES:
        try:
            items = source.fetch(limit=3)  # проверим несколько последних
        except Exception as e:
            print(f"Failed to fetch from {source.name}: {e}")
            continue

        for item in items:
            if db.seen(item.url):
                continue

            post_text = generate_post(item.title, item.url, item.summary)

            if DRY_RUN:
                print("=== TEST POST ===")
                print(post_text)
                print("=================")
                return

            success = send_post(post_text)
            if success:
                db.add_if_absent(item.url, item.title,
                                 source.name, item.published_at)
                db.mark_posted(item.url)
                print(f"Posted news from {source.name}: {item.title}")
                return  # публикуем только 1 новость за запуск


def run_youtube():
    db = DB()
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        order="date",
        maxResults=1   # только последнее видео
    )
    response = request.execute()

    for item in response.get("items", []):
        if item["id"]["kind"] != "youtube#video":
            continue

        video_id = item["id"]["videoId"]
        video_title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        published_at = item["snippet"]["publishedAt"]

        # проверяем — публиковалось ли это видео
        if db.seen(video_url):
            print(f"Already posted video: {video_url}")
            return

        # публикуем только если видео вышло сегодня
        published_date = datetime.strptime(
            published_at, "%Y-%m-%dT%H:%M:%SZ").date()
        today = datetime.utcnow().date()

        if published_date < today:
            print(f"Video is older than today: {video_url}")
            return

        post_text = f"Новое видео на YouTube:\n\n{video_title}\n{video_url}"

        if DRY_RUN:
            print("=== TEST POST ===")
            print(post_text)
            print("=================")
            return

        success = send_post(post_text)
        if success:
            db.add_if_absent(video_url, video_title, "YouTube", published_at)
            db.mark_posted(video_url)
            print(f"Posted YouTube video: {video_title}")


if __name__ == "__main__":
    print("=== Running MLBB News + YouTube Bot ===")
    run_news()
    run_youtube()
    print("=== Run finished ===")
