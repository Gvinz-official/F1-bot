import html

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.i18n import t
from bot.services.f1_client import F1Client
from bot.utils.dates import format_dt, parse_dt

router = Router()


async def build_next_text(f1: F1Client, tz_name, lang):
    race = await f1.get_next_race()
    if race is None:
        return t(lang, "next_waiting")
    location = race.get("Circuit", {}).get("Location", {})
    return t(
        lang, "next_text",
        race=html.escape(race.get("raceName", "")),
        place=html.escape(location.get("locality", t(lang, "unknown"))),
        country=html.escape(location.get("country", t(lang, "unknown"))),
        quali=format_dt(parse_dt(race.get("Qualifying")), tz_name, lang),
        race_time=format_dt(parse_dt(race), tz_name, lang),
        tz=tz_name,
    )


@router.message(Command("next"))
async def next_command(message: Message, f1: F1Client, lang: str, tz: str):
    await message.answer(await build_next_text(f1, tz, lang))
