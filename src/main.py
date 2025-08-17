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
    print(f"🔍 Ищем видео для героя {hero_name}...")
    
    # Пробуем разные варианты поиска
    search_queries = [
        hero_name,  # Точное имя
        f"{hero_name} MLBB",  # Имя + MLBB
        f"{hero_name} Mobile Legends",  # Имя + Mobile Legends
        f"{hero_name} tutorial",  # Имя + tutorial
        f"{hero_name} guide",  # Имя + guide
        f"{hero_name} gameplay",  # Имя + gameplay
    ]
    
    for query in search_queries:
        print(f"  🔎 Пробуем поиск: '{query}'")
        
        try:
            request = youtube.search().list(
                part="snippet",
                channelId=YOUTUBE_CHANNEL_ID,
                q=query,
                order="relevance",
                maxResults=5  # Увеличиваем количество результатов
            )
            response = request.execute()
            items = response.get("items", [])
            
            # Ищем видео среди результатов
            for item in items:
                if item["id"]["kind"] != "youtube#video":
                    continue
                    
                video_id = item["id"]["videoId"]
                video_title = item["snippet"]["title"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Проверяем, содержит ли название героя или похожие слова
                title_lower = video_title.lower()
                hero_lower = hero_name.lower()
                
                if (hero_lower in title_lower or 
                    any(word in title_lower for word in ["mlbb", "mobile legends", "tutorial", "guide", "gameplay"])):
                    
                    print(f"✅ Найдено видео: {video_title}")
                    return video_title, video_url, item["snippet"]["publishedAt"]
            
        except Exception as e:
            print(f"  ⚠️ Ошибка поиска для '{query}': {e}")
            continue
    
    print(f"❌ Видео для героя {hero_name} не найдено")
    print("💡 Попробуйте:")
    print("   - Проверить правильность YOUTUBE_CHANNEL_ID")
    print("   - Убедиться, что на канале есть видео по MLBB")
    print("   - Проверить, что API ключ имеет доступ к каналу")
    return None


def run_hero_post():
    print("🚀 Запускаем MLBB Hero Trick Bot...")
    
    # Проверяем конфигурацию
    if not YOUTUBE_API_KEY:
        print("❌ Отсутствует YOUTUBE_API_KEY")
        return
    
    if not YOUTUBE_CHANNEL_ID:
        print("❌ Отсутствует YOUTUBE_CHANNEL_ID")
        return
    
    try:
        db = DB()
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        print("✅ YouTube API подключен успешно")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return

    hero = pick_new_hero(db)
    print(f"🎯 Выбран герой: {hero}")

    video_data = find_hero_video(youtube, hero)
    if not video_data:
        print(f"⚠️ Видео по герою {hero} не найдено")
        return

    video_title, video_url, published_at = video_data

    # Проверяем — публиковалось ли это видео
    if db.seen(f"hero:{hero}"):
        print(f"ℹ️ Герой {hero} уже был опубликован")
        return

    print(f"🤖 Начинаем генерацию поста для {hero}...")
    
    # Генерируем пост через AI
    try:
        post_text = generate_hero_post(hero=hero, video_url=video_url)
        print(f"✅ Пост сгенерирован успешно!")
        
        if DRY_RUN:
            print("=== TEST POST ===")
            print(post_text)
            print("=================")
            return
        else:
            print("📤 Отправляем пост в Telegram...")
            success = send_post(post_text)
            
            if success:
                db.add_if_absent(f"hero:{hero}", hero, "HeroTrick", published_at)
                db.mark_posted(f"hero:{hero}")
                print(f"✅ Опубликован пост с героем {hero}")
            else:
                print(f"❌ Ошибка при публикации поста с героем {hero}")
                
    except Exception as e:
        print(f"❌ Ошибка при генерации поста: {e}")
        print("🔍 Проверьте настройки ИИ и API ключи")


if __name__ == "__main__":
    print("=== Running MLBB Hero Trick Bot ===")
    run_hero_post()
    print("=== Run finished ===")
