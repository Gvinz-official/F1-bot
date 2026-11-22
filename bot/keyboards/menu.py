from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot import config
from bot.i18n import t


class MenuCallback(CallbackData, prefix="menu"):
    action: str


class LangCallback(CallbackData, prefix="lang"):
    code: str


def _btn(lang, key, action):
    return InlineKeyboardButton(
        text=t(lang, key), callback_data=MenuCallback(action=action).pack()
    )


def app_button(lang):
    return InlineKeyboardButton(text=t(lang, "btn_app"), web_app=WebAppInfo(url=config.WEBAPP_URL))


def app_markup(lang):
    if not config.WEBAPP_URL:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[app_button(lang)]])


def main_menu(lang):
    rows = [
        [_btn(lang, "btn_next", "next"), _btn(lang, "btn_results", "results")],
        [_btn(lang, "btn_standings", "standings")],
    ]
    if config.WEBAPP_URL:
        rows.insert(0, [app_button(lang)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def standings_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(lang, "btn_drivers", "drivers"), _btn(lang, "btn_constructors", "constructors")],
        [_btn(lang, "btn_back", "main")],
    ])


def back_menu(lang, target="main"):
    return InlineKeyboardMarkup(inline_keyboard=[[_btn(lang, "btn_back", target)]])


def lang_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇬🇧 English", callback_data=LangCallback(code="en").pack()),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data=LangCallback(code="ru").pack()),
    ]])
