#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации бота
"""

import os
from dotenv import load_dotenv

def check_config():
    """Проверяем конфигурацию бота"""
    print("🔍 Проверяем конфигурацию MLBB News Bot...")
    print("=" * 50)
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Список необходимых переменных
    required_vars = {
        "TELEGRAM_BOT_TOKEN": "Telegram Bot Token",
        "TELEGRAM_CHANNEL": "Telegram Channel Username", 
        "OPENROUTER_API_KEY": "OpenRouter API Key",
        "YOUTUBE_API_KEY": "YouTube API Key",
        "YOUTUBE_CHANNEL_ID": "YouTube Channel ID"
    }
    
    optional_vars = {
        "OPENROUTER_MODEL": "OpenRouter Model (default: gpt-4o-mini)",
        "LANGUAGE": "Language (default: en)",
        "DRY_RUN": "Dry Run Mode (default: false)"
    }
    
    print("📋 Обязательные переменные:")
    missing_required = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Скрываем полное значение для безопасности
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"  ✅ {description}: {masked_value}")
        else:
            print(f"  ❌ {description}: НЕ НАЙДЕНА")
            missing_required.append(var)
    
    print("\n📋 Опциональные переменные:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {description}: {value}")
        else:
            print(f"  ⚠️  {description}: не задана (будет использовано значение по умолчанию)")
    
    print("\n" + "=" * 50)
    
    if missing_required:
        print("❌ КРИТИЧЕСКИЕ ОШИБКИ:")
        for var in missing_required:
            print(f"   - Отсутствует {var}")
        print("\n📝 Создайте файл .env в корне проекта с необходимыми переменными")
        print("📖 Смотрите README.MD для инструкций по настройке")
        return False
    else:
        print("✅ Все обязательные переменные настроены!")
        print("🚀 Бот готов к запуску")
        return True

def test_openrouter_connection():
    """Тестируем подключение к OpenRouter"""
    print("\n🤖 Тестируем подключение к OpenRouter...")
    
    try:
        from config import client, OPENROUTER_MODEL
        
        # Простой тест API
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "user", "content": "Say 'Hello' in one word"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenRouter API работает! Ответ: '{result}'")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к OpenRouter: {e}")
        print("🔍 Проверьте:")
        print("   - Правильность OPENROUTER_API_KEY")
        print("   - Наличие кредитов на OpenRouter")
        print("   - Доступность API OpenRouter")
        return False

if __name__ == "__main__":
    config_ok = check_config()
    
    if config_ok:
        test_openrouter_connection()
    
    print("\n" + "=" * 50)
    if config_ok:
        print("🎉 Конфигурация проверена успешно!")
    else:
        print("💥 Обнаружены проблемы с конфигурацией")
