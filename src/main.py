from config import POST_LIMIT_PER_RUN, DRY_RUN
from storage.db import DB
from ai.generator import generate_post
from publisher.telegram_client import send_post
from sources.ml_official import MLOfficialNews
from sources.gamerbraves import GamerBravesML
import time
import sys
import os

# Добавляем путь для корректного импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


SOURCES = [MLOfficialNews(), GamerBravesML()]


def run_once():
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
                return

            success = send_post(post_text)
            if success:
                db.add_if_absent(item.url, item.title,
                                 source.name, item.published_at)
                db.mark_posted(item.url)
                posted_count += 1

            if posted_count >= POST_LIMIT_PER_RUN:
                print("Reached post limit for this run.")
                return


if __name__ == "__main__":
    while True:
        print("=== Checking for new news ===")
        run_once()
        print("Sleeping for 4 hours...")
        time.sleep(4 * 60 * 60)  # 4 часа
