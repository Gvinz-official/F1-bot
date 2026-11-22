from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from bot.config import DEFAULT_TIMEZONE

MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
           "августа", "сентября", "октября", "ноября", "декабря"],
}

# ключ сессии -> ключи в ответе Jolpica/Ergast
SESSION_FIELDS = [
    ("fp1", "FirstPractice"),
    ("fp2", "SecondPractice"),
    ("fp3", "ThirdPractice"),
    ("sprint_quali", "SprintQualifying"),
    ("sprint_quali", "SprintShootout"),
    ("sprint", "Sprint"),
    ("quali", "Qualifying"),
]


def parse_dt(data):
    if not isinstance(data, dict):
        return None
    date = data.get("date")
    time = data.get("time")
    if not date or not time:
        return None
    try:
        dt = datetime.fromisoformat(f"{date}T{time}")
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def to_iso(dt):
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def valid_tz(name):
    if not isinstance(name, str) or not name or len(name) > 64:
        return False
    try:
        ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        return False
    return True


def race_sessions(race):
    """[(key, datetime)] по возрастанию времени; гонка идёт ключом 'race'."""
    out = {}
    for key, field in SESSION_FIELDS:
        dt = parse_dt(race.get(field))
        if dt:
            out[key] = dt
    race_dt = parse_dt(race)
    if race_dt:
        out["race"] = race_dt
    return sorted(out.items(), key=lambda kv: kv[1])


def format_dt(dt, tz_name, lang="en"):
    if dt is None:
        return "TBA"
    tz_name = tz_name if valid_tz(tz_name) else DEFAULT_TIMEZONE
    local = dt.astimezone(ZoneInfo(tz_name))
    months = MONTHS.get(lang, MONTHS["en"])
    return f"{local:%H:%M}, {local.day} {months[local.month - 1]}"
