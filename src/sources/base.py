from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NewsItem:
    title: str
    url: str
    published_at: Optional[str] = None
    summary: Optional[str] = None


class BaseSource:
    name: str = "base"

    def fetch(self, limit: int = 5) -> List[NewsItem]:
        raise NotImplementedError
