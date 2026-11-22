"""Проверка initData мини-приложения (алгоритм из документации Telegram)."""
import hashlib
import hmac
import json
import time
from operator import itemgetter
from urllib.parse import parse_qsl

MAX_AGE_SECONDS = 48 * 3600


def validate_init_data(init_data, bot_token, now=None):
    """-> dict пользователя Telegram или None, если подпись неверна/устарела."""
    if not init_data or len(init_data) > 4096:
        return None
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None
    received = parsed.pop("hash", None)
    if not received:
        return None
    check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items(), key=itemgetter(0)))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received):
        return None
    try:
        auth_date = int(parsed.get("auth_date", "0"))
        user = json.loads(parsed["user"])
        user["id"] = int(user["id"])
    except (ValueError, KeyError, TypeError):
        return None
    if (now or time.time()) - auth_date > MAX_AGE_SECONDS:
        return None
    return user
