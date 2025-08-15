import requests
from bs4 import BeautifulSoup
from typing import List
from .base import BaseSource, NewsItem
from utils import absolutize


class MLOfficialNews(BaseSource):
    name = "ml_official"
    BASE = "https://m.mobilelegends.com"
    URL = "https://m.mobilelegends.com/en/news"

    def fetch(self, limit: int = 5) -> List[NewsItem]:
        r = requests.get(self.URL, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        items: List[NewsItem] = []

        # Ищем карточки новостей — широкая эвристика
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            title = (a.get_text(strip=True) or "")
            if not href or not title:
                continue
            # Берём только раздел news
            if "/en/news" not in href:
                continue
            url = absolutize(self.BASE, href)
            # Фильтр на повторяющиеся / пустые заголовки
            if len(title) < 6:
                continue
            items.append(NewsItem(title=title, url=url))

        # Удалим дубликаты по URL и обрежем по limit
        seen = set()
        unique = []
        for it in items:
            if it.url in seen:
                continue
            seen.add(it.url)
            unique.append(it)
        return unique[:limit]
