import asyncio
import logging

from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import CallbackQuery

log = logging.getLogger(__name__)


async def edit_or_ignore(callback: CallbackQuery, text, reply_markup=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


async def safe_send(bot, db, chat_id, text, reply_markup=None):
    """Отправка без падений: заблокировавших бота отключаем от рассылки."""
    for attempt in range(2):
        try:
            await bot.send_message(chat_id, text, reply_markup=reply_markup)
            return True
        except TelegramForbiddenError:
            await db.set_notify(chat_id, 0)
            return False
        except TelegramRetryAfter as e:
            if attempt:
                return False
            await asyncio.sleep(e.retry_after + 1)
        except TelegramAPIError as e:
            log.warning("Не удалось отправить сообщение %s: %s", chat_id, e)
            return False
    return False
