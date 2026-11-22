from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.handlers.races import build_next_text
from bot.handlers.stats import build_constructors_text, build_results_text, build_standings_text
from bot.i18n import t
from bot.keyboards.menu import MenuCallback, back_menu, main_menu, standings_menu
from bot.services.f1_client import F1Client
from bot.utils.telegram import edit_or_ignore

router = Router()


@router.message(Command("menu"))
async def menu_command(message: Message, lang: str):
    await message.answer(t(lang, "menu_title"), reply_markup=main_menu(lang))


@router.callback_query(MenuCallback.filter(F.action == "main"))
async def main_callback(callback: CallbackQuery, lang: str):
    await edit_or_ignore(callback, t(lang, "menu_title"), reply_markup=main_menu(lang))
    await callback.answer()


@router.callback_query(MenuCallback.filter(F.action == "next"))
async def next_callback(callback: CallbackQuery, f1: F1Client, lang: str, tz: str):
    text = await build_next_text(f1, tz, lang)
    await edit_or_ignore(callback, text, reply_markup=back_menu(lang))
    await callback.answer()


@router.callback_query(MenuCallback.filter(F.action == "results"))
async def results_callback(callback: CallbackQuery, f1: F1Client, lang: str):
    await edit_or_ignore(callback, await build_results_text(f1, lang), reply_markup=back_menu(lang))
    await callback.answer()


@router.callback_query(MenuCallback.filter(F.action == "standings"))
async def standings_callback(callback: CallbackQuery, lang: str):
    await edit_or_ignore(callback, t(lang, "standings_choose"), reply_markup=standings_menu(lang))
    await callback.answer()


@router.callback_query(MenuCallback.filter(F.action == "drivers"))
async def drivers_callback(callback: CallbackQuery, f1: F1Client, lang: str):
    text = await build_standings_text(f1, lang)
    await edit_or_ignore(callback, text, reply_markup=back_menu(lang, "standings"))
    await callback.answer()


@router.callback_query(MenuCallback.filter(F.action == "constructors"))
async def constructors_callback(callback: CallbackQuery, f1: F1Client, lang: str):
    text = await build_constructors_text(f1, lang)
    await edit_or_ignore(callback, text, reply_markup=back_menu(lang, "standings"))
    await callback.answer()
