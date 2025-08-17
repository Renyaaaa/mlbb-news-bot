#!/usr/bin/env python3
"""
Тестовый скрипт для проверки генератора ИИ
"""

import os
from dotenv import load_dotenv
from ai.generator import generate_hero_post

def test_ai_generator():
    """Тестируем генератор ИИ"""
    print("🧪 Тестируем генератор ИИ...")
    
    # Проверяем переменные окружения
    load_dotenv()
    
    required_vars = [
        "OPENROUTER_API_KEY",
        "TELEGRAM_BOT_TOKEN", 
        "TELEGRAM_CHANNEL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("📝 Создайте файл .env в корне проекта с необходимыми переменными")
        print("📖 Смотрите README.MD для инструкций по настройке")
        return False
    
    print("✅ Все необходимые переменные окружения найдены")
    
    # Тестируем генерацию поста
    test_hero = "Layla"
    test_video_url = "https://www.youtube.com/watch?v=test123"
    
    print(f"🤖 Генерируем пост для героя: {test_hero}")
    print(f"📹 Тестовое видео: {test_video_url}")
    print("-" * 50)
    
    try:
        post = generate_hero_post(test_hero, test_video_url)
        print("✅ Генерация успешна!")
        print("📝 Сгенерированный пост:")
        print("-" * 50)
        print(post)
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при генерации: {e}")
        print("🔍 Проверьте:")
        print("   - Правильность OPENROUTER_API_KEY")
        print("   - Наличие кредитов на OpenRouter")
        print("   - Доступность API OpenRouter")
        return False

if __name__ == "__main__":
    success = test_ai_generator()
    if success:
        print("\n🎉 Тест прошел успешно! ИИ работает корректно.")
    else:
        print("\n💥 Тест не прошел. Проверьте настройки и попробуйте снова.")
