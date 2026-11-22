import html
import logging

from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from bot import config
from bot.db import Database
from bot.i18n import t
from bot.keyboards.menu import LangCallback, app_markup, lang_menu, main_menu

log = logging.getLogger(__name__)
router = Router()


async def _handle_referral(message: Message, bot: Bot, db: Database, user: dict, lang: str, arg: str):
    """Ссылка вида ?start=ref_<id> делает двух людей друзьями и даёт бонус."""
    if not (arg and arg.startswith("ref_") and arg[4:].isdigit()):
        return
    inviter_id = int(arg[4:])
    if inviter_id == user["id"]:
        return
    inviter = await db.get_user(inviter_id)
    if not inviter or not await db.add_friends(user["id"], inviter_id):
        return
    await db.add_coins(user["id"], config.REF_BONUS)
    await db.add_coins(inviter_id, config.REF_BONUS)
    await message.answer(
        t(lang, "ref_joined", name=html.escape(inviter["name"]), coins=config.REF_BONUS)
    )
    try:
        await bot.send_message(
            inviter_id,
            t(inviter["lang"], "ref_joined", name=html.escape(user["name"]), coins=config.REF_BONUS),
        )
    except Exception:
        log.debug("Не удалось уведомить пригласившего %s", inviter_id)


@router.message(CommandStart())
async def start_command(message: Message, command: CommandObject, bot: Bot, db: Database, user: dict, lang: str):
    await _handle_referral(message, bot, db, user, lang, command.args or "")
    await message.answer(t(lang, "start").strip(), reply_markup=main_menu(lang))


@router.message(Command("help"))
async def help_command(message: Message, lang: str):
    await message.answer(t(lang, "help").strip())


@router.message(Command("about"))
async def about_command(message: Message, lang: str):
    await message.answer(t(lang, "about").strip())


@router.message(Command("app"))
async def app_command(message: Message, lang: str):
    if not config.WEBAPP_URL:
        await message.answer(t(lang, "app_unavailable"))
        return
    await message.answer(t(lang, "app_open"), reply_markup=app_markup(lang))


@router.message(Command("lang"))
async def lang_command(message: Message, lang: str):
    await message.answer(t(lang, "lang_choose"), reply_markup=lang_menu())


@router.callback_query(LangCallback.filter())
async def lang_callback(callback: CallbackQuery, callback_data: LangCallback, db: Database, user: dict):
    code = callback_data.code
    if code not in config.LANGS:
        await callback.answer()
        return
    await db.set_lang(user["id"], code)
    await callback.message.edit_text(t(code, "lang_set"), reply_markup=main_menu(code))
    await callback.answer()


@router.message(Command("notify"))
async def notify_command(message: Message, db: Database, user: dict, lang: str):
    enabled = not user["notify"]
    await db.set_notify(user["id"], enabled)
    await message.answer(t(lang, "notify_on" if enabled else "notify_off"))
