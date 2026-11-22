import asyncio
import html

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.i18n import DIVIDER, t
from bot.services.f1_client import F1Client

router = Router()


async def build_standings_text(f1: F1Client, lang):
    standings = await f1.get_standings()
    if not standings:
        return t(lang, "waiting_season")
    lines = [t(lang, "drivers_title"), DIVIDER]
    for row in standings:
        driver = html.escape(row["Driver"]["familyName"])
        team = html.escape(row["Constructors"][-1]["name"])
        lines.append(f"<b>{row['position']}. {driver} </b><i>( {team} )</i><b> - </b> {row['points']}")
    return "\n".join(lines)


async def build_constructors_text(f1: F1Client, lang):
    standings = await f1.get_constructor_standings()
    if not standings:
        return t(lang, "waiting_season")
    lines = [t(lang, "constructors_title"), DIVIDER]
    wins_word = t(lang, "wins")
    for row in standings:
        team = html.escape(row["Constructor"]["name"])
        lines.append(
            f"<b>{row['position']}. {team} </b><i>( {row['wins']} {wins_word} )</i><b> - </b> {row['points']}"
        )
    return "\n".join(lines)


async def build_results_text(f1: F1Client, lang):
    race = await f1.get_last_results()
    if race is None:
        return t(lang, "results_empty")
    lines = [f"🏁 <b>{html.escape(race['raceName'])}</b>", DIVIDER]
    for row in race["Results"][:10]:
        driver = html.escape(row["Driver"]["familyName"])
        team = html.escape(row["Constructor"]["name"])
        lines.append(f"<b>{row['position']}. {driver} </b><i>( {team} )</i><b> - </b> {row['points']}")
    return "\n".join(lines)


async def build_driver_text(f1: F1Client, query: str, lang):
    standings = await f1.get_standings()
    query = query.strip().lower()
    matches = [
        row for row in standings
        if query in row["Driver"]["familyName"].lower()
        or query in row["Driver"]["givenName"].lower()
        or query == (row["Driver"].get("code") or "").lower()
    ]
    if not matches:
        return t(lang, "driver_not_found", query=html.escape(query))
    if len(matches) > 1:
        names = [html.escape(row["Driver"]["familyName"]) for row in matches]
        return f"{t(lang, 'driver_many')} {', '.join(names)}"
    row = matches[0]
    d = row["Driver"]
    return t(
        lang, "driver_card",
        name=html.escape(f"{d['givenName']} {d['familyName']}"),
        code=d.get("code", "—"),
        nat=html.escape(d.get("nationality", "—")),
        team=html.escape(row["Constructors"][-1]["name"]),
        pos=row["position"], wins=row["wins"], points=row["points"],
    )


@router.message(Command("driver"))
async def driver_command(message: Message, command: CommandObject, f1: F1Client, lang: str):
    query = command.args
    if not query:
        await message.answer(t(lang, "driver_usage"))
        return
    if len(query) > 30:
        await message.answer(t(lang, "driver_too_long"))
        return
    await message.answer(await build_driver_text(f1, query, lang))


@router.message(Command("results"))
async def results_command(message: Message, f1: F1Client, lang: str):
    await message.answer(await build_results_text(f1, lang))


@router.message(Command("standings"))
async def standings_command(message: Message, f1: F1Client, lang: str):
    await message.answer(await build_standings_text(f1, lang))


@router.message(Command("constructors"))
async def constructors_command(message: Message, f1: F1Client, lang: str):
    await message.answer(await build_constructors_text(f1, lang))


if __name__ == "__main__":

    async def check():
        f1 = F1Client()
        print(await build_standings_text(f1, "ru"))
        await f1.close()

    asyncio.run(check())
