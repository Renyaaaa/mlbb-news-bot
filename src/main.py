import sys
import os
from sources.gamerbraves import GamerBravesML
from sources.ml_official import MLOfficialNews
from publisher.telegram_client import send_post
from ai.generator import generate_post
from storage.db import DB
from config import POST_LIMIT_PER_RUN, DRY_RUN

# YouTube
from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID

# Добавляем путь для корректного импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SOURCES = [MLOfficialNews(), GamerBravesML()]


def run_news():
    db = DB()
    posted_count = 0

    for source in SOURCES:
        try:
            items = source.fetch(limit=POST_LIMIT_PER_RUN)
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
                continue

            success = send_post(post_text)
            if success:
                db.add_if_absent(item.url, item.title,
                                 source.name, item.published_at)
                db.mark_posted(item.url)
                posted_count += 1

            if posted_count >= POST_LIMIT_PER_RUN:
                print("Reached post limit for news.")
                return


def run_youtube():
    db = DB()
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        order="date",
        maxResults=POST_LIMIT_PER_RUN
    )
    response = request.execute()

    for item in response.get("items", []):
        if item["id"]["kind"] != "youtube#video":
            continue
        video_id = item["id"]["videoId"]
        video_title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        if db.seen(video_id):
            continue

        post_text = f"Новое видео на YouTube:\n\n{video_title}\n{video_url}"

        if DRY_RUN:
            print("=== TEST POST ===")
            print(post_text)
            print("=================")
            continue

        success = send_post(post_text)
        if success:
            db.add_if_absent(video_id, video_title, "YouTube",
                             item["snippet"]["publishedAt"])
            db.mark_posted(video_id)


if __name__ == "__main__":
    print("=== Running MLBB News + YouTube Bot ===")
    run_news()
    run_youtube()
    print("=== Run finished ===")
