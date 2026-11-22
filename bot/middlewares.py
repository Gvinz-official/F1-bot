from aiogram import BaseMiddleware

from bot.config import DEFAULT_LANG, DEFAULT_TIMEZONE


class UserMiddleware(BaseMiddleware):
    """Создаёт/обновляет пользователя в БД и кладёт user, lang, tz в данные хендлера."""

    def __init__(self, db):
        self.db = db

    async def __call__(self, handler, event, data):
        tg_user = data.get("event_from_user")
        if tg_user and not tg_user.is_bot:
            user = await self.db.upsert_user(
                tg_user.id, tg_user.full_name, tg_user.username, tg_user.language_code
            )
            data["user"] = user
            data["lang"] = user["lang"]
            data["tz"] = user["tz"] or DEFAULT_TIMEZONE
        else:
            data["lang"] = DEFAULT_LANG
            data["tz"] = DEFAULT_TIMEZONE
        return await handler(event, data)
