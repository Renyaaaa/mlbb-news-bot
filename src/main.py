from sources.gamerbraves import GamerBravesML
from sources.ml_official import MLOfficialNews
from publisher.telegram_client import send_post
from ai.generator import generate_post
from storage.db import DB
from config import POST_LIMIT_PER_RUN, DRY_RUN
from flask import Flask
import threading
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


def loop_every_4_hours():
    while True:
        print("=== Checking for new news ===")
        run_once()
        print("Sleeping for 4 hours...")
        time.sleep(4 * 60 * 60)


# Создаём поток для фонового выполнения
threading.Thread(target=loop_every_4_hours, daemon=True).start()

# Flask-приложение, чтобы контейнер не останавливался
app = Flask(__name__)


@app.route("/")
def index():
    return "Bot is running!"


if __name__ == "__main__":
    # В Railway обычно порт 8080
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
