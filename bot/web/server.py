"""aiohttp-сервер: отдаёт мини-приложение (webapp/) и JSON API для него."""
import json
import logging
import random
import re
import secrets
import time
from datetime import datetime, timedelta, timezone

import httpx
from aiohttp import web

from bot.config import (
    DEV_MODE,
    LANGS,
    MAX_BET,
    MIN_BET,
    REACTION_DAILY_CAP,
    WEBAPP_DIR,
)
from bot.services import game
from bot.services.models import norm_constructor, norm_result, norm_standing
from bot.utils.dates import parse_dt, race_sessions, to_iso, valid_tz
from bot.web.auth import validate_init_data

log = logging.getLogger(__name__)

DB = web.AppKey("db", object)
F1 = web.AppKey("f1", object)
TOKEN = web.AppKey("token", str)
BOT_USERNAME = web.AppKey("bot_username", str)
REACTION_TOKENS = web.AppKey("reaction_tokens", dict)

ID_RE = re.compile(r"^[a-z0-9_]{1,40}$")
LIGHTS_MS = 3000  # пять огней загораются по одному за 600 мс


# ---------- утилиты ----------
def ok(data=None, status=200):
    return web.json_response(
        data if data is not None else {}, status=status,
        dumps=lambda o: json.dumps(o, ensure_ascii=False),
    )


def err(code, status=400):
    return ok({"error": code}, status)


async def read_json(request):
    try:
        data = await request.json()
    except Exception:
        data = None
    if not isinstance(data, dict):
        raise web.HTTPBadRequest(
            text=json.dumps({"error": "bad_json"}), content_type="application/json"
        )
    return data


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def pretty_id(driver_id):
    return driver_id.replace("_", " ").title()


def race_view(race, now=None):
    now = now or datetime.now(timezone.utc)
    race_dt = parse_dt(race)
    loc = race["Circuit"]["Location"]
    if race_dt:
        done = race_dt + timedelta(hours=3) < now
    else:
        done = race["date"] < now.date().isoformat()
    return {
        "season": race["season"],
        "round": int(race["round"]),
        "name": race["raceName"],
        "circuit": race["Circuit"]["circuitName"],
        "place": loc["locality"],
        "country": loc["country"],
        "date": race["date"],
        "start": to_iso(race_dt),
        "sessions": [{"key": k, "at": to_iso(dt)} for k, dt in race_sessions(race)],
        "done": done,
    }


def bet_view(bet, names):
    return {
        "id": bet["id"],
        "round": bet["round"],
        "season": bet["season"],
        "race": bet["race_name"],
        "kind": bet["kind"],
        "pick": bet["pick"],
        "pick_name": names.get(bet["pick"], pretty_id(bet["pick"])),
        "opponent_name": names.get(bet["opponent"], pretty_id(bet["opponent"]))
        if bet["opponent"] else "",
        "stake": bet["stake"],
        "odds": bet["odds"],
        "status": bet["status"],
        "payout": bet["payout"],
    }


async def load_standings(app):
    return [norm_standing(r) for r in await app[F1].get_standings()]


async def load_markets(app):
    f1 = app[F1]
    standings = await f1.get_standings()
    fallback = [] if standings else await f1.get_season_drivers()
    return game.build_markets(game.drivers_for_markets(standings, fallback))


def reaction_reward(ms):
    if ms < 200:
        return 40
    if ms < 250:
        return 30
    if ms < 300:
        return 20
    if ms < 400:
        return 10
    return 5


# ---------- middleware ----------
@web.middleware
async def errors_mw(request, handler):
    try:
        return await handler(request)
    except web.HTTPException:
        raise
    except httpx.HTTPError as e:
        log.warning("F1 API недоступен: %s", e)
        return err("upstream", 502)
    except Exception:
        log.exception("Ошибка в %s", request.path)
        return err("server", 500)


@web.middleware
async def auth_mw(request, handler):
    if not request.path.startswith("/api/"):
        return await handler(request)
    app = request.app
    header = request.headers.get("Authorization", "")
    user = None
    if header.startswith("tma "):
        user = validate_init_data(header[4:], app[TOKEN])
    elif DEV_MODE:
        try:
            dev_id = int(request.headers.get("X-Dev-User", "1"))
        except ValueError:
            dev_id = 1
        user = {"id": dev_id, "first_name": f"Dev {dev_id}", "language_code": "en"}
    if not user:
        return err("unauthorized", 401)
    name = " ".join(p for p in (user.get("first_name"), user.get("last_name")) if p)
    request["user"] = await app[DB].upsert_user(
        user["id"], name, user.get("username"), user.get("language_code")
    )
    return await handler(request)


async def no_cache(request, response):
    response.headers["Cache-Control"] = "no-store" if request.path.startswith("/api/") else "no-cache"


# ---------- страницы ----------
async def index(request):
    return web.FileResponse(WEBAPP_DIR / "index.html")


async def health(request):
    return ok({"ok": True})


# ---------- профиль ----------
async def api_me(request):
    app, u = request.app, request["user"]
    today = datetime.now(timezone.utc).date().isoformat()
    username = app.get(BOT_USERNAME, "")
    friends = await app[DB].friend_ids(u["id"])
    return ok({
        "id": u["id"],
        "name": u["name"],
        "lang": u["lang"],
        "tz": u["tz"],
        "notify": bool(u["notify"]),
        "coins": u["coins"],
        "streak": u["streak"],
        "daily_available": u["last_daily"] != today,
        "best_reaction": u["best_reaction"],
        "friends": len(friends),
        "invite_link": f"https://t.me/{username}?start=ref_{u['id']}" if username else "",
        "limits": {"min_bet": MIN_BET, "max_bet": MAX_BET},
        "plays_left": await app[DB].reaction_plays_left(u["id"], REACTION_DAILY_CAP),
    })


async def api_settings(request):
    u, db = request["user"], request.app[DB]
    body = await read_json(request)
    if "lang" in body:
        if body["lang"] not in LANGS:
            return err("bad_lang")
        await db.set_lang(u["id"], body["lang"])
    if "notify" in body:
        if not isinstance(body["notify"], bool):
            return err("bad_notify")
        await db.set_notify(u["id"], body["notify"])
    if "tz" in body and body["tz"]:
        if not valid_tz(body["tz"]):
            return err("bad_tz")
        await db.set_tz(u["id"], body["tz"])
    return ok()


async def api_daily(request):
    result = await request.app[DB].claim_daily(request["user"]["id"])
    if result is None:
        return err("already_claimed", 409)
    return ok(result)


# ---------- данные о сезоне ----------
async def api_calendar(request):
    f1 = request.app[F1]
    now = datetime.now(timezone.utc)
    races = [race_view(r, now) for r in await f1.get_schedule()]
    nxt = await f1.get_next_race()
    return ok({"races": races, "next_round": int(nxt["round"]) if nxt else None})


async def api_last(request):
    last = await request.app[F1].get_last_results()
    if not last:
        return ok({"race": None, "rows": []})
    return ok({
        "race": {"season": last["season"], "round": int(last["round"]),
                 "name": last["raceName"], "date": last["date"]},
        "rows": [norm_result(r) for r in last["Results"]],
    })


async def api_standings_drivers(request):
    return ok({"rows": await load_standings(request.app)})


async def api_standings_teams(request):
    rows = await request.app[F1].get_constructor_standings()
    return ok({"rows": [norm_constructor(r) for r in rows]})


async def api_driver(request):
    driver_id = request.match_info["id"]
    if not ID_RE.match(driver_id):
        return err("bad_id")
    app = request.app
    current = next((d for d in await load_standings(app) if d["id"] == driver_id), None)
    try:
        career = await app[F1].get_driver_career(driver_id)
    except httpx.HTTPError:
        career = None
    return ok({"current": current, "career": career})


async def api_team(request):
    team_id = request.match_info["id"]
    if not ID_RE.match(team_id):
        return err("bad_id")
    app = request.app
    rows = [norm_constructor(r) for r in await app[F1].get_constructor_standings()]
    current = next((r for r in rows if r["id"] == team_id), None)
    drivers = [d for d in await load_standings(app) if d["team_id"] == team_id]
    try:
        career = await app[F1].get_constructor_career(team_id)
    except httpx.HTTPError:
        career = None
    return ok({"current": current, "drivers": drivers, "career": career})


# ---------- ставки ----------
async def api_markets(request):
    app, u = request.app, request["user"]
    race = await app[F1].get_next_race()
    if not race:
        return ok({"race": None})
    markets = await load_markets(app)
    names = {e["id"]: e["name"] for e in markets["winner"]}
    mine = await app[DB].user_bets(u["id"], season=race["season"], rnd=race["round"])
    closes = game.betting_closes_at(race)
    return ok({
        "race": race_view(race),
        "open": game.is_betting_open(race),
        "closes_at": to_iso(closes),
        "markets": markets,
        "my_bets": [bet_view(b, names) for b in mine],
        "coins": u["coins"],
    })


async def api_bet(request):
    app, u = request.app, request["user"]
    body = await read_json(request)
    kind, pick, stake = body.get("kind"), body.get("pick"), body.get("stake")
    ref = body.get("ref") or ""
    if kind not in game.KINDS or not isinstance(pick, str) or not isinstance(ref, str):
        return err("bad_request")
    if not is_int(stake) or not MIN_BET <= stake <= MAX_BET:
        return err("bad_stake")
    race = await app[F1].get_next_race()
    if not race or not game.is_betting_open(race):
        return err("closed", 409)
    markets = await load_markets(app)
    selection = game.find_selection(markets, kind, pick, ref if kind == "h2h" else "")
    if selection is None:
        return err("bad_pick")
    odds, opponent, ref = selection
    status, coins = await app[DB].place_bet(
        u["id"], race["season"], int(race["round"]), race["raceName"],
        kind, pick, ref, opponent, stake, odds,
    )
    if status != "ok":
        return err(status, 409)
    return ok({"coins": coins, "odds": odds})


async def api_bet_history(request):
    app, u = request.app, request["user"]
    standings = await load_standings(app)
    names = {d["id"]: d["name"] for d in standings}
    bets = await app[DB].user_bets(u["id"], limit=40)
    return ok({"bets": [bet_view(b, names) for b in bets]})


# ---------- игра «Старт» ----------
async def api_reaction_start(request):
    app, u = request.app, request["user"]
    tokens = app[REACTION_TOKENS]
    now = time.monotonic()
    for key in [k for k, v in tokens.items() if now - v[1] > 120]:
        tokens.pop(key, None)
    delay = random.randint(900, 2800)
    token = secrets.token_urlsafe(12)
    tokens[token] = (u["id"], now, delay)
    return ok({
        "token": token, "delay_ms": delay, "lights_ms": LIGHTS_MS,
        "plays_left": await app[DB].reaction_plays_left(u["id"], REACTION_DAILY_CAP),
    })


async def api_reaction_finish(request):
    app, u = request.app, request["user"]
    body = await read_json(request)
    ms = body.get("reaction_ms")
    entry = app[REACTION_TOKENS].pop(body.get("token"), None)
    if entry is None or entry[0] != u["id"] or not is_int(ms):
        return err("bad_token")
    _, started, delay = entry
    elapsed = (time.monotonic() - started) * 1000
    if not 100 <= ms <= 5000 or elapsed < LIGHTS_MS + delay + ms - 150:
        return err("invalid_time")
    result = await app[DB].record_reaction(
        u["id"], ms, reaction_reward(ms), REACTION_DAILY_CAP
    )
    result["reaction_ms"] = ms
    return ok(result)


# ---------- рейтинг ----------
async def api_leaderboard(request):
    app, u = request.app, request["user"]
    scope = request.query.get("scope", "global")
    board = request.query.get("board", "coins")
    if scope not in ("global", "friends") or board not in ("coins", "reaction"):
        return err("bad_request")
    ids = None
    if scope == "friends":
        ids = list(await app[DB].friend_ids(u["id"])) + [u["id"]]
    rows = await app[DB].leaderboard(board, ids, 20)
    rank = await app[DB].user_rank(u["id"], board, ids)
    return ok({
        "rows": [
            {"rank": r["rank"], "name": r["name"], "value": r["value"], "me": r["id"] == u["id"]}
            for r in rows
        ],
        "me_rank": rank,
    })


def create_app(token, db, f1, bot_username=""):
    app = web.Application(middlewares=[errors_mw, auth_mw], client_max_size=64 * 1024)
    app[TOKEN] = token
    app[DB] = db
    app[F1] = f1
    app[BOT_USERNAME] = bot_username
    app[REACTION_TOKENS] = {}
    app.on_response_prepare.append(no_cache)

    r = app.router
    r.add_get("/", index)
    r.add_get("/healthz", health)
    r.add_get("/api/me", api_me)
    r.add_post("/api/settings", api_settings)
    r.add_post("/api/daily", api_daily)
    r.add_get("/api/calendar", api_calendar)
    r.add_get("/api/last", api_last)
    r.add_get("/api/standings/drivers", api_standings_drivers)
    r.add_get("/api/standings/teams", api_standings_teams)
    r.add_get("/api/driver/{id}", api_driver)
    r.add_get("/api/team/{id}", api_team)
    r.add_get("/api/markets", api_markets)
    r.add_post("/api/bets", api_bet)
    r.add_get("/api/bets/history", api_bet_history)
    r.add_post("/api/reaction/start", api_reaction_start)
    r.add_post("/api/reaction/finish", api_reaction_finish)
    r.add_get("/api/leaderboard", api_leaderboard)
    r.add_static("/static/", WEBAPP_DIR, show_index=False)
    return app
