import asyncio
import hashlib
from dataclasses import dataclass

import feedparser

from config import RSS_SOURCES


@dataclass
class NewsItem:
    source: str
    title: str
    link: str
    summary: str
    published: str

    @property
    def item_id(self) -> str:
        raw = self.link or (self.title + self.published)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _parse_feed(url: str):
    return feedparser.parse(url)


async def fetch_source(name: str, url: str) -> list[NewsItem]:
    feed = await asyncio.to_thread(_parse_feed, url)
    items = []
    for entry in feed.entries:
        items.append(
            NewsItem(
                source=name,
                title=getattr(entry, "title", "") or "",
                link=getattr(entry, "link", "") or "",
                summary=getattr(entry, "summary", "") or "",
                published=getattr(entry, "published", "") or "",
            )
        )
    return items


async def fetch_all() -> list[NewsItem]:
    tasks = [fetch_source(name, url) for name, url in RSS_SOURCES]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_items: list[NewsItem] = []
    for res in results:
        if isinstance(res, Exception):
            continue
        all_items.extend(res)
    return all_items
