import html
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import storage
from config import BOT_TOKEN, CHECK_INTERVAL_MINUTES, MAX_ITEMS_PER_CHECK, TARGET_CHAT_ID
from fetcher import NewsItem, fetch_all
from filters import is_relevant

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def format_item(item: NewsItem) -> str:
    title = html.escape(item.title)
    source = html.escape(item.source)
    return f"📰 <b>{title}</b>\nИсточник: {source}\n{item.link}"


async def collect_new_relevant_items(limit: int | None = None) -> list[NewsItem]:
    items = await fetch_all()
    fresh = []
    for item in items:
        if storage.is_seen(item.item_id):
            continue
        if not is_relevant(item.title, item.summary):
            continue
        fresh.append(item)

    # убираем дубликаты одной и той же новости из разных лент
    seen_links = set()
    unique = []
    for item in fresh:
        if item.link and item.link in seen_links:
            continue
        seen_links.add(item.link)
        unique.append(item)

    if limit:
        unique = unique[:limit]
    return unique


async def scheduled_check(context: ContextTypes.DEFAULT_TYPE):
    if not TARGET_CHAT_ID:
        logger.warning("TARGET_CHAT_ID не задан — автоматическая рассылка выключена")
        return

    items = await collect_new_relevant_items(limit=MAX_ITEMS_PER_CHECK)
    for item in items:
        try:
            await context.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=format_item(item),
                parse_mode="HTML",
            )
        except Exception:
            logger.exception("Не удалось отправить новость: %s", item.title)
            continue
        storage.mark_seen(item.item_id, item.source, item.title, item.link)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я собираю новости по нефти, санкциям, войне на Украине, "
        "Ирану и ресурсным «голубым фишкам» России и США (РБК, ТАСС, "
        "Lenta.ru, OilPrice.com).\n\n"
        "Команды:\n"
        "/news — свежие новости по теме прямо сейчас\n"
        "/id — узнать ID этого чата (нужно для настройки автопостинга)\n"
    )


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID этого чата: `{update.effective_chat.id}`", parse_mode="Markdown")


async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ищу свежие новости...")
    items = await collect_new_relevant_items(limit=MAX_ITEMS_PER_CHECK)
    if not items:
        await update.message.reply_text("Новых подходящих новостей не найдено.")
        return
    for item in items:
        await update.message.reply_text(format_item(item), parse_mode="HTML")
        storage.mark_seen(item.item_id, item.source, item.title, item.link)


def main():
    if not BOT_TOKEN:
        raise SystemExit("Не задан BOT_TOKEN в .env — см. README.md")

    storage.init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("id", cmd_id))
    app.add_handler(CommandHandler("news", cmd_news))

    app.job_queue.run_repeating(
        scheduled_check,
        interval=CHECK_INTERVAL_MINUTES * 60,
        first=10,
    )

    logger.info("Бот запущен, проверка каждые %s минут", CHECK_INTERVAL_MINUTES)
    app.run_polling()


if __name__ == "__main__":
    main()
