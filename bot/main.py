import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from aiohttp import web

from bot import config
from bot.db import Database
from bot.handlers import common, menu, races, stats
from bot.keyboards.menu import app_markup
from bot.middlewares import UserMiddleware
from bot.services.f1_client import F1Client
from bot.services.notifier import Notifier
from bot.utils.telegram import safe_send
from bot.web.server import create_app

log = logging.getLogger(__name__)

COMMANDS = {
    "en": [
        ("start", "Start the bot"), ("app", "Open the mini app"), ("menu", "Main menu"),
        ("next", "Next Grand Prix"), ("results", "Latest results"),
        ("standings", "Driver standings"), ("constructors", "Constructor standings"),
        ("driver", "Driver card"), ("lang", "Change language"),
        ("notify", "Reminders on/off"), ("help", "All commands"), ("about", "About"),
    ],
    "ru": [
        ("start", "Запустить бота"), ("app", "Открыть мини-приложение"), ("menu", "Главное меню"),
        ("next", "Следующий Гран-при"), ("results", "Последние результаты"),
        ("standings", "Личный зачёт"), ("constructors", "Кубок конструкторов"),
        ("driver", "Карточка пилота"), ("lang", "Сменить язык"),
        ("notify", "Напоминания вкл/выкл"), ("help", "Все команды"), ("about", "О боте"),
    ],
}


async def setup_bot(bot: Bot):
    try:
        await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS["en"]])
        await bot.set_my_commands(
            [BotCommand(command=c, description=d) for c, d in COMMANDS["ru"]], language_code="ru"
        )
        if config.WEBAPP_URL:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="🏎 F1", web_app=WebAppInfo(url=config.WEBAPP_URL))
            )
    except Exception:
        log.exception("Не удалось настроить команды и кнопку меню")


async def keepalive(url):
    """Раз в 10 минут обращается к собственному адресу: бесплатный Render усыпляет
    сервис после 15 минут без входящих запросов."""
    async with httpx.AsyncClient(timeout=20) as client:
        while True:
            await asyncio.sleep(600)
            try:
                await client.get(url + "/healthz")
            except Exception as e:
                log.warning("Самопинг не удался: %s", e)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not config.BOT_TOKEN:
        raise SystemExit("BOT_TOKEN не найден. Проверь файл .env")
    if config.WEBAPP_URL and not config.WEBAPP_URL.startswith("https://"):
        log.warning("WEBAPP_URL должен начинаться с https:// — мини-приложение отключено")
        config.WEBAPP_URL = ""
    if not config.WEBAPP_URL:
        log.warning("WEBAPP_URL не задан: бот работает, но кнопки мини-приложения не показываются")

    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    db = Database(config.DATABASE_URL or config.DB_PATH)
    f1 = F1Client()

    dp = Dispatcher(f1=f1, db=db)
    dp.message.outer_middleware(UserMiddleware(db))
    dp.callback_query.outer_middleware(UserMiddleware(db))
    dp.include_router(common.router)
    dp.include_router(races.router)
    dp.include_router(menu.router)
    dp.include_router(stats.router)

    me = await bot.get_me()
    runner = web.AppRunner(create_app(config.BOT_TOKEN, db, f1, me.username or ""))
    await runner.setup()
    await web.TCPSite(runner, config.WEB_HOST, config.WEB_PORT).start()
    log.info("Мини-приложение слушает http://%s:%s", config.WEB_HOST, config.WEB_PORT)

    async def send(user_id, text, lang):
        await safe_send(bot, db, user_id, text, reply_markup=app_markup(lang))

    notifier_task = asyncio.create_task(Notifier(db, f1, send).run())
    keepalive_task = asyncio.create_task(keepalive(config.KEEPALIVE_URL)) if config.KEEPALIVE_URL else None
    await setup_bot(bot)
    try:
        await dp.start_polling(bot)
    finally:
        notifier_task.cancel()
        if keepalive_task:
            keepalive_task.cancel()
        await runner.cleanup()
        await f1.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
