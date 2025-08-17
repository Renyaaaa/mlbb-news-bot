#!/usr/bin/env python3
"""
Тестовый скрипт для проверки поиска видео на YouTube
"""

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

def test_youtube_search():
    """Тестируем поиск видео на YouTube"""
    print("🧪 Тестируем поиск видео на YouTube...")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем необходимые переменные
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    youtube_channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    
    if not youtube_api_key:
        print("❌ Отсутствует YOUTUBE_API_KEY")
        return False
    
    if not youtube_channel_id:
        print("❌ Отсутствует YOUTUBE_CHANNEL_ID")
        return False
    
    print(f"✅ YouTube API Key: {youtube_api_key[:20]}...")
    print(f"✅ YouTube Channel ID: {youtube_channel_id}")
    
    try:
        # Создаем YouTube API клиент
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        print("✅ YouTube API клиент создан успешно")
        
        # Тестируем поиск по каналу
        print(f"\n🔍 Тестируем поиск по каналу {youtube_channel_id}...")
        
        # Сначала попробуем найти любые видео на канале
        request = youtube.search().list(
            part="snippet",
            channelId=youtube_channel_id,
            q="MLBB",  # Ищем любые видео с MLBB
            order="relevance",
            maxResults=10
        )
        
        response = request.execute()
        items = response.get("items", [])
        
        if not items:
            print("❌ На канале не найдено видео с запросом 'MLBB'")
            print("💡 Возможные причины:")
            print("   - Неправильный YOUTUBE_CHANNEL_ID")
            print("   - На канале нет видео по MLBB")
            print("   - API ключ не имеет доступа к каналу")
            return False
        
        print(f"✅ Найдено {len(items)} результатов")
        
        # Показываем найденные видео
        print("\n📹 Найденные видео:")
        for i, item in enumerate(items[:5], 1):
            if item["id"]["kind"] == "youtube#video":
                title = item["snippet"]["title"]
                video_id = item["id"]["videoId"]
                url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"  {i}. {title}")
                print(f"     {url}")
        
        # Тестируем поиск конкретного героя
        test_hero = "Layla"
        print(f"\n🎯 Тестируем поиск героя: {test_hero}")
        
        search_queries = [
            test_hero,
            f"{test_hero} MLBB",
            f"{test_hero} tutorial"
        ]
        
        for query in search_queries:
            print(f"  🔎 Поиск: '{query}'")
            
            request = youtube.search().list(
                part="snippet",
                channelId=youtube_channel_id,
                q=query,
                order="relevance",
                maxResults=3
            )
            
            response = request.execute()
            items = response.get("items", [])
            
            if items:
                print(f"    ✅ Найдено {len(items)} результатов")
                for item in items[:2]:
                    if item["id"]["kind"] == "youtube#video":
                        title = item["snippet"]["title"]
                        print(f"      - {title}")
            else:
                print(f"    ❌ Результатов не найдено")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при работе с YouTube API: {e}")
        return False

if __name__ == "__main__":
    success = test_youtube_search()
    if success:
        print("\n🎉 Тест YouTube поиска прошел успешно!")
    else:
        print("\n💥 Тест YouTube поиска не прошел!")
