# News Bot — бот новостей по нефти, войне и ресурсным голубым фишкам

Собирает новости из открытых RSS-лент (РБК, ТАСС, Lenta.ru, OilPrice.com),
фильтрует по ключевым словам (нефть, санкции, Украина, Иран, ОПЕК, а также
тикеры/названия ресурсных компаний РФ и США) и:

- шлёт подходящие новости автоматически в чат/канал по расписанию;
- по команде `/news` показывает свежие новости прямо сейчас.

## 1. Создание бота и получение токена

1. В Telegram напишите **@BotFather**.
2. Отправьте команду `/newbot`.
3. Придумайте имя бота (любое) и username (должен заканчиваться на `bot`,
   например `oil_geo_news_bot`).
4. BotFather пришлёт токен вида `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxx`.
   Это и есть `BOT_TOKEN`.

## 2. Установка

Нужен Python 3.11+.

```bash
cd news_bot
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Откройте `.env` и вставьте туда токен:

```
BOT_TOKEN=123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 3. Первый запуск и получение TARGET_CHAT_ID

`TARGET_CHAT_ID` — это чат/канал, куда бот будет автоматически слать новости
по расписанию. Пока его нет, автопостинг просто не работает, но команда
`/news` уже доступна.

Чтобы узнать ID:

- **Личный чат с ботом**: запустите бота (`python bot.py`), напишите ему
  `/start`, затем `/id` — он покажет ID вашего личного чата.
- **Группа**: добавьте бота в группу, напишите там `/id`.
- **Канал**: добавьте бота **администратором** канала, перешлите любое
  сообщение из канала в бота (в личку) — либо временно добавьте бота в канал
  как участника и напишите `/id` там (для каналов ID обычно вида
  `-100XXXXXXXXXX`).

Скопируйте полученное число в `.env`:

```
TARGET_CHAT_ID=-1001234567890
```

и перезапустите бота.

## 4. Запуск

```bash
python bot.py
```

Бот будет проверять источники каждые `CHECK_INTERVAL_MINUTES` минут
(по умолчанию 20) и слать новые подходящие новости в `TARGET_CHAT_ID`.

## 5. Постоянная работа (чтобы не запускать вручную)

### Вариант А: systemd (Linux-сервер)

Создайте файл `/etc/systemd/system/news_bot.service`:

```ini
[Unit]
Description=News Bot
After=network.target

[Service]
WorkingDirectory=/путь/до/news_bot
ExecStart=/путь/до/news_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
sudo systemctl daemon-reload
sudo systemctl enable news_bot
sudo systemctl start news_bot
sudo journalctl -u news_bot -f   # логи
```

### Вариант Б: screen/tmux (быстрый вариант для теста)

```bash
tmux new -s news_bot
python bot.py
# Ctrl+B, затем D — чтобы отключиться, оставив процесс работать
```

### Вариант В: Railway (без своего сервера)

Бот — это фоновый процесс (не веб-сервер), поэтому в проекте уже лежит
`Procfile` со строкой `worker: python bot.py` — Railway по нему поймёт,
что не нужно ждать HTTP-порт.

1. **Залейте код в GitHub.** Создайте пустой репозиторий на GitHub и
   запушьте туда папку `news_bot` (можно через веб-интерфейс GitHub —
   "Add file → Upload files" — если не хочется работать с git).

2. **Создайте проект на Railway.** На [railway.com](https://railway.com)
   → New Project → **Deploy from GitHub repo** → выберите свой репозиторий.
   Railway сам увидит `requirements.txt` и `Procfile` и соберёт билд.

3. **Добавьте переменные окружения.** В сервисе откройте вкладку
   **Variables** и добавьте:
   ```
   BOT_TOKEN=токен_от_BotFather
   CHECK_INTERVAL_MINUTES=20
   MAX_ITEMS_PER_CHECK=8
   DB_PATH=/data/news_bot.db
   ```
   `TARGET_CHAT_ID` пока можно оставить пустым — добавите на шаге 5.

4. **Подключите постоянное хранилище (Volume).** Без этого SQLite-база
   будет стираться при каждом новом деплое. В сервисе: вкладка
   **Settings → Volumes → New Volume**, mount path укажите `/data`.
   Именно поэтому в переменных выше `DB_PATH=/data/news_bot.db` —
   файл должен лежать внутри примонтированного volume.

5. **Деплой и получение chat_id.** Railway развернёт бота автоматически.
   Откройте вкладку **Deployments → View Logs** — там будет строка
   "Бот запущен...". Дальше как обычно: напишите боту `/start`, затем
   `/id` в нужном чате/канале, скопируйте число, впишите его как
   `TARGET_CHAT_ID` в Variables на Railway — сервис перезапустится
   автоматически и подтянет новое значение.

6. **Готово.** Railway держит процесс запущенным постоянно и сам
   перезапускает его при сбое. Логи всегда доступны во вкладке
   Deployments.

> Если код не на GitHub, а только локально — можно развернуть и без
> репозитория через Railway CLI: `npm i -g @railway/cli`, затем
> `railway login`, `railway init`, `railway up` из папки `news_bot`.

## 6. Настройка фильтров и источников

Всё — в `config.py`:

- `RSS_SOURCES` — список лент `(название, url)`. Можно добавлять свои.
- `COMPANY_KEYWORDS` — компании/тикеры, которые считаются «голубыми фишками».
- `GEO_KEYWORDS` — слова про войну/геополитику (Украина, Иран, санкции, ОПЕК…).
- `OIL_KEYWORDS` — слова про нефть/энергетику в целом.

Новость считается подходящей, если в заголовке или описании встретилось
**хотя бы одно** слово из любого из трёх списков. Чем шире списки — тем
больше новостей будет приходить (и наоборот).

`CHECK_INTERVAL_MINUTES` и `MAX_ITEMS_PER_CHECK` (сколько новостей максимум
слать за одну проверку) — в `.env`.

## 7. Про Bloomberg

У Bloomberg нет открытого RSS с полными статьями, а сайт защищён от
парсинга — включить его как обычный источник нельзя. Если у вас есть
платный доступ к Bloomberg Terminal/API, его можно подключить отдельным
модулем в `fetcher.py` — скажите, и я помогу это добавить.

## 8. Структура проекта

```
news_bot/
├── bot.py           # команды и запуск бота
├── config.py        # токен, источники, ключевые слова
├── fetcher.py        # получение и парсинг RSS
├── filters.py         # фильтрация по ключевым словам
├── storage.py         # SQLite, чтобы не дублировать новости
├── requirements.txt
├── Procfile            # для Railway/Heroku — запуск как фонового процесса
├── .env.example
└── README.md
```
