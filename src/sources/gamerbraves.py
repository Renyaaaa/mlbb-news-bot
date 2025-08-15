import requests
from bs4 import BeautifulSoup
from typing import List
from .base import BaseSource, NewsItem


class GamerBravesML(BaseSource):
    name = "gamerbraves"
    URL = "https://www.gamerbraves.com/tag/mobile-legends/"

    def fetch(self, limit: int = 5) -> List[NewsItem]:
        r = requests.get(self.URL, timeout=20, headers={
                         "User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        items: List[NewsItem] = []
        # Ищем карточки постов в ленте
        for card in soup.select("article a[href]"):
            href = card.get("href")
            title = card.get_text(strip=True)
            if not href or not title:
                continue
            # Отбрасываем навигационные/внутренние ссылки без заголовков
            if len(title) < 8:
                continue
            items.append(NewsItem(title=title, url=href))

        # Дедуп и лимит
        seen = set()
        unique = []
        for it in items:
            if it.url in seen:
                continue
            seen.add(it.url)
            unique.append(it)
        return unique[:limit]
