import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
WEBAPP_DIR = BASE_DIR / "webapp"

BOT_TOKEN = os.getenv("BOT_TOKEN")
_PORT = os.getenv("PORT")  # на Render задаётся автоматически
RENDER_URL = (os.getenv("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
WEBAPP_URL = (os.getenv("WEBAPP_URL") or RENDER_URL).strip().rstrip("/")
# Адрес, который бот сам опрашивает раз в 10 минут, чтобы бесплатный хостинг не усыплял сервис
KEEPALIVE_URL = (os.getenv("KEEPALIVE_URL") or RENDER_URL).strip().rstrip("/")
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0" if _PORT else "127.0.0.1")
WEB_PORT = int(_PORT or os.getenv("WEB_PORT", "8080"))
# Если задан DATABASE_URL (Postgres), база живёт там, иначе в локальном файле SQLite
DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "data" / "f1bot.sqlite3"))
DEV_MODE = os.getenv("DEV_MODE") == "1"

HTTP_TIMEOUT = 10
HTTP_RETRIES = 3

CACHE_TTL_DAY = 86400
CACHE_TTL_LONG = 3600
CACHE_TTL_SHORT = 300

BASE = "https://api.jolpi.ca/ergast/f1"

DEFAULT_TIMEZONE = "Asia/Tashkent"
DEFAULT_LANG = "en"
LANGS = ("en", "ru")

# --- виртуальная экономика (реальных денег в боте нет) ---
START_COINS = 1000
DAILY_BONUS = 200
DAILY_STREAK_STEP = 50       # + за каждый день серии (до 6 дней)
REF_BONUS = 100              # обоим при добавлении в друзья
MIN_BET = 10
MAX_BET = 500

# --- мини-игра на реакцию ---
REACTION_DAILY_CAP = 8       # сколько игр в день приносят монеты
