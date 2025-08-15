import hashlib
from urllib.parse import urljoin


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def absolutize(base: str, href: str) -> str:
    return urljoin(base, href)
