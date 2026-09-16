import os
from dotenv import load_dotenv

load_dotenv()

# --- Основные настройки (берутся из .env) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID", "")  # куда слать новости автоматически
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "20"))
MAX_ITEMS_PER_CHECK = int(os.getenv("MAX_ITEMS_PER_CHECK", "8"))
DB_PATH = os.getenv("DB_PATH", "news_bot.db")

# --- Источники RSS: (название, url) ---
# Можно свободно добавлять свои источники сюда.
RSS_SOURCES = [
    ("РБК", "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"),
    ("ТАСС", "https://tass.com/rss/v2.xml"),
    ("Lenta.ru", "https://lenta.ru/rss"),
    ("OilPrice.com", "https://oilprice.com/rss/main"),
]

# --- Ключевые слова: компании (ресурсные "голубые фишки" РФ и США) ---
COMPANY_KEYWORDS = [
    # Россия
    "газпром", "роснефт", "лукойл", "новатэк", "татнефт", "сургутнефтегаз",
    "транснефт", "норникель", "северстал", "нлмк", "ммк", "алроса",
    "русал", "полюс", "полиметалл",
    # США
    "exxon", "эксон", "chevron", "шеврон", "conocophillips",
    "occidental petroleum", "schlumberger", " slb ", "halliburton",
    "freeport-mcmoran", "newmont",
]

# --- Ключевые слова: геополитика / война, влияющие на нефть ---
GEO_KEYWORDS = [
    "украин", " сво ", "иран", "израил", "ближний восток", "ормузск",
    "hormuz", "санкц", "sanction", "опек", "opec", "нефтепровод",
    "нефтяной терминал", "ракетн", "удар по", "атака на", "эскалац",
]

# --- Ключевые слова: нефть / энергетика в целом ---
OIL_KEYWORDS = [
    "нефт", "brent", "wti", "баррел", "barrel", " газ ", "спг", "lng",
    "энергетик", "energy market", " oil ", " oil,", "oil price", "crude",
]

ALL_KEYWORDS = COMPANY_KEYWORDS + GEO_KEYWORDS + OIL_KEYWORDS
