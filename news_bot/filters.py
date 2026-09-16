from config import ALL_KEYWORDS


def normalize(text: str) -> str:
    return (text or "").lower()


def matches_keywords(title: str, summary: str = "") -> list[str]:
    """Возвращает список ключевых слов, найденных в тексте."""
    text = f" {normalize(title)} {normalize(summary)} "
    found = [kw for kw in ALL_KEYWORDS if kw.strip().lower() in text]
    return found


def is_relevant(title: str, summary: str = "") -> bool:
    return len(matches_keywords(title, summary)) > 0
