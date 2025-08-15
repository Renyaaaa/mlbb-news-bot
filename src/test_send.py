from publisher.telegram_client import send_post

# Тестовый пост
post_text = """
=== TEST POST ===
Mobile Legends Developer Moonton Wins Defamation Lawsuit Against Tencent

https://www.gamerbraves.com/mobile-legends-developer-moonton-wins-defamation-lawsuit-against-tencent/
=================
"""

# Отправляем
success = send_post(post_text)

if success:
    print("Post sent successfully!")
else:
    print("Failed to send post.")
