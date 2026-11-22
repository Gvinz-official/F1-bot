"""Запуск: python -m tests.test_backend  (нужны aiohttp, httpx, python-dotenv)."""
import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from aiohttp.test_utils import TestClient, TestServer

from bot.db import Database
from bot.services import game
from bot.services.notifier import Notifier
from bot.utils.dates import parse_dt
from bot.web import server
from bot.web.auth import validate_init_data

TOKEN = "123456:TEST"
NOW = datetime.now(timezone.utc)


def iso_parts(dt):
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S") + "Z"


def sess(dt):
    d, t = iso_parts(dt)
    return {"date": d, "time": t}


def make_race(rnd, race_dt):
    d, t = iso_parts(race_dt)
    return {
        "season": "2026", "round": str(rnd), "raceName": f"Test GP {rnd}",
        "Circuit": {"circuitName": "Circuit", "Location": {"locality": "Town", "country": "Land"}},
        "date": d, "time": t,
        "FirstPractice": sess(race_dt - timedelta(days=2)),
        "Qualifying": sess(race_dt - timedelta(days=1)),
    }


def drv(i):
    return {"driverId": f"d{i}", "code": f"D{i}", "permanentNumber": str(i),
            "givenName": "Name", "familyName": f"Fam{i}", "nationality": "X"}


def standing(i):
    return {"position": str(i), "points": str(100 - i * 10), "wins": str(max(3 - i, 0)),
            "Driver": drv(i),
            "Constructors": [{"constructorId": f"t{(i + 1) // 2}", "name": f"Team{(i + 1) // 2}"}]}


def result(i, pos, grid=None):
    return {"position": str(pos), "grid": str(grid or pos), "points": "0", "status": "Finished",
            "Time": {"time": "1:30:00"}, "Driver": drv(i),
            "Constructor": {"constructorId": f"t{(i + 1) // 2}", "name": f"Team{(i + 1) // 2}"}}


class FakeF1:
    def __init__(self):
        self.past = make_race(1, NOW - timedelta(days=7))
        self.future = make_race(2, NOW + timedelta(days=7))

    async def get_schedule(self): return [self.past, self.future]
    async def get_next_race(self): return self.future
    async def get_standings(self): return [standing(i) for i in range(1, 7)]
    async def get_season_drivers(self): return []
    async def get_constructor_standings(self):
        return [{"position": str(i), "points": "50", "wins": "1",
                 "Constructor": {"constructorId": f"t{i}", "name": f"Team{i}", "nationality": "X"}}
                for i in (1, 2, 3)]
    async def get_last_results(self):
        r = dict(self.past)
        r["Results"] = [result(1, 1), result(2, 2), result(3, 3), result(4, 4)]
        return r
    async def get_race_results(self, season, rnd):
        # d2 победил, d1 второй, d4 третий, d3 — не финишировал в зачёте дуэли (нет в списке)
        r = dict(self.past)
        r["Results"] = [result(2, 1, grid=3), result(1, 2, grid=2), result(4, 3, grid=1)]
        return r if str(rnd) == "1" else None
    async def get_qualifying(self, season, rnd):
        return [{"position": "1", "Driver": drv(4)}]
    async def get_driver_career(self, driver_id):
        return {"seasons": 3, "titles": 1, "wins": 5, "points": 300, "best": 1, "first": "2024", "history": []}
    async def get_constructor_career(self, cid):
        return {"seasons": 10, "titles": 2, "wins": 9, "points": 900, "best": 1, "first": "2016", "history": []}


def init_data(user_id, name="Tester", token=TOKEN, age=0):
    fields = {"auth_date": str(int(time.time()) - age), "query_id": "AAA",
              "user": json.dumps({"id": user_id, "first_name": name, "language_code": "ru"})}
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


def hdr(user_id, **kw):
    return {"Authorization": "tma " + init_data(user_id, **kw)}


async def main():
    # --- auth ---
    assert validate_init_data(init_data(7), TOKEN)["id"] == 7
    assert validate_init_data(init_data(7), "other:token") is None
    assert validate_init_data(init_data(7).replace("Tester", "Hacker"), TOKEN) is None
    assert validate_init_data(init_data(7, age=3 * 86400), TOKEN) is None
    print("auth ok")

    db = Database(":memory:")
    f1 = FakeF1()
    app = server.create_app(TOKEN, db, f1, "f1testbot")
    client = TestClient(TestServer(app))
    await client.start_server()
    try:
        assert (await client.get("/api/me")).status == 401
        assert (await client.get("/healthz")).status == 200
        r = await client.get("/")
        assert r.status == 200 and "no-cache" in r.headers["Cache-Control"]

        # --- профиль ---
        me = await (await client.get("/api/me", headers=hdr(1))).json()
        assert me["coins"] == 1000 and me["lang"] == "ru" and me["daily_available"]
        assert me["invite_link"] == "https://t.me/f1testbot?start=ref_1"
        r = await client.post("/api/settings", json={"lang": "en", "notify": False, "tz": "Asia/Tashkent"}, headers=hdr(1))
        assert r.status == 200
        me = await (await client.get("/api/me", headers=hdr(1))).json()
        assert me["lang"] == "en" and me["notify"] is False and me["tz"] == "Asia/Tashkent"
        assert (await client.post("/api/settings", json={"tz": "Mars/Base"}, headers=hdr(1))).status == 400
        assert (await client.post("/api/settings", json={"lang": "de"}, headers=hdr(1))).status == 400
        d1 = await (await client.post("/api/daily", headers=hdr(1))).json()
        assert d1["bonus"] == 200 and d1["streak"] == 1 and d1["coins"] == 1200
        assert (await client.post("/api/daily", headers=hdr(1))).status == 409
        print("profile ok")

        # --- данные ---
        cal = await (await client.get("/api/calendar", headers=hdr(1))).json()
        assert len(cal["races"]) == 2 and cal["next_round"] == 2
        assert cal["races"][0]["done"] and not cal["races"][1]["done"]
        assert [s["key"] for s in cal["races"][1]["sessions"]] == ["fp1", "quali", "race"]
        last = await (await client.get("/api/last", headers=hdr(1))).json()
        assert last["rows"][0]["code"] == "D1"
        st = await (await client.get("/api/standings/drivers", headers=hdr(1))).json()
        assert st["rows"][0]["team_id"] == "t1" and st["rows"][0]["points"] == 90
        tm = await (await client.get("/api/team/t1", headers=hdr(1))).json()
        assert len(tm["drivers"]) == 2 and tm["career"]["titles"] == 2
        dr = await (await client.get("/api/driver/d3", headers=hdr(1))).json()
        assert dr["current"]["name"] == "Name Fam3" and dr["career"]["wins"] == 5
        assert (await client.get("/api/driver/BAD!ID", headers=hdr(1))).status in (400, 404)
        print("data ok")

        # --- рынки и ставки ---
        mk = await (await client.get("/api/markets", headers=hdr(1))).json()
        assert mk["open"] and len(mk["markets"]["winner"]) == 6 and len(mk["markets"]["h2h"]) == 3
        odds = {e["id"]: e["odds"] for e in mk["markets"]["winner"]}
        assert odds["d1"] < odds["d6"], "лидер должен иметь меньший коэффициент"
        assert all(1.1 <= o <= 99 for o in odds.values())
        pod = {e["id"]: e["odds"] for e in mk["markets"]["podium"]}
        assert all(pod[k] < odds[k] for k in odds), "подиум должен быть дешевле победы"

        async def bet(uid, **body):
            return await client.post("/api/bets", json=body, headers=hdr(uid))

        r = await bet(1, kind="winner", pick="d1", stake=500)
        assert r.status == 200, await r.text()
        assert (await r.json())["coins"] == 700
        assert (await bet(1, kind="winner", pick="d2", stake=100)).status == 409  # дубль
        assert (await bet(1, kind="winner", pick="zzz", stake=100)).status == 400
        assert (await bet(1, kind="winner", pick="d1", stake=5)).status == 400
        assert (await bet(1, kind="winner", pick="d1", stake=9999)).status == 400
        assert (await bet(1, kind="winner", pick="d1", stake="100")).status == 400
        assert (await bet(1, kind="winner", pick="d1", stake=True)).status == 400
        assert (await bet(1, kind="podium", pick="d2", stake=500)).status == 200
        r = await bet(1, kind="pole", pick="d4", stake=500)
        assert r.status == 409 and (await r.json())["error"] == "no_funds"
        h = await bet(1, kind="h2h", pick="d1", ref="t1", stake=100)
        assert h.status == 200
        assert (await bet(1, kind="h2h", pick="d5", ref="t1", stake=100)).status == 400
        mk = await (await client.get("/api/markets", headers=hdr(1))).json()
        assert len(mk["my_bets"]) == 3 and mk["coins"] == 100
        print("bets ok")

        # --- расчёт ---
        # ставки пользователя 1 переносим на раунд 1 (прошедший), где известны результаты
        db._store._db.conn.execute("UPDATE bets SET round=1")
        db._store._db.conn.commit()
        await db.get_user(1)
        await db.upsert_user(2, "Second", None, "en")
        await db.place_bet(2, "2026", 1, "Test GP 1", "pole", "d4", "", "", 100, 5.0)
        await db.place_bet(2, "2026", 1, "Test GP 1", "h2h", "d3", "t2", "d4", 100, 2.0)  # d3 нет в результатах -> void
        settled = await game.settle_pending(db, f1)
        by = {(b["user_id"], b["kind"]): b for b in settled}
        assert by[(1, "winner")]["status"] == "lost"      # победил d2
        assert by[(1, "podium")]["status"] == "won"       # d2 на подиуме
        assert by[(1, "h2h")]["status"] == "lost"         # d2 финишировал выше d1
        assert by[(2, "pole")]["status"] == "won"         # поул у d4
        assert by[(2, "h2h")]["status"] == "void"         # d3 нет в результатах -> возврат
        assert await game.settle_pending(db, f1) == [], "повторный расчёт ничего не меняет"
        u1, u2 = await db.get_user(1), await db.get_user(2)
        podium_odds = next(b for b in settled if b["user_id"] == 1 and b["kind"] == "podium")["payout"]
        assert u1["coins"] == 100 + podium_odds
        assert u2["coins"] == 1000 - 200 + 500 + 100      # pole x5.0 и возврат дуэли
        print("settle ok")

        # --- игра на реакцию ---
        r = await client.post("/api/reaction/start", headers=hdr(1))
        st = await r.json()
        assert 900 <= st["delay_ms"] <= 2800 and st["lights_ms"] == 3000
        # слишком быстрый ответ (клиент «соврал») отклоняется
        r = await client.post("/api/reaction/finish", json={"token": st["token"], "reaction_ms": 150}, headers=hdr(1))
        assert r.status == 400
        st = await (await client.post("/api/reaction/start", headers=hdr(1))).json()
        tok = app[server.REACTION_TOKENS]
        uid, started, delay = tok[st["token"]]
        tok[st["token"]] = (uid, started - 10, delay)       # «прошло» 10 секунд
        r = await client.post("/api/reaction/finish", json={"token": st["token"], "reaction_ms": 230}, headers=hdr(1))
        fin = await r.json()
        assert r.status == 200 and fin["rewarded"] and fin["reward"] == 30 and fin["best"] == 230
        # токен одноразовый
        r = await client.post("/api/reaction/finish", json={"token": st["token"], "reaction_ms": 230}, headers=hdr(1))
        assert r.status == 400
        # чужой токен
        st = await (await client.post("/api/reaction/start", headers=hdr(1))).json()
        r = await client.post("/api/reaction/finish", json={"token": st["token"], "reaction_ms": 300}, headers=hdr(2))
        assert r.status == 400
        # дневной лимит наград
        for _ in range(10):
            st = await (await client.post("/api/reaction/start", headers=hdr(2))).json()
            uid, started, delay = tok[st["token"]]
            tok[st["token"]] = (uid, started - 10, delay)
            fin = await (await client.post("/api/reaction/finish", json={"token": st["token"], "reaction_ms": 280}, headers=hdr(2))).json()
        assert fin["rewarded"] is False and fin["plays_left"] == 0
        print("reaction ok")

        # --- друзья и рейтинг ---
        assert await db.add_friends(1, 2) is True and await db.add_friends(2, 1) is False
        lb = await (await client.get("/api/leaderboard?scope=global&board=coins", headers=hdr(1))).json()
        assert [r["rank"] for r in lb["rows"]] == [1, 2] and sum(r["me"] for r in lb["rows"]) == 1
        fr = await (await client.get("/api/leaderboard?scope=friends&board=reaction", headers=hdr(1))).json()
        assert fr["rows"][0]["value"] == 230 and fr["me_rank"] == 1
        await db.upsert_user(3, "Loner", None, "en")
        lone = await (await client.get("/api/leaderboard?scope=friends&board=coins", headers=hdr(3))).json()
        assert len(lone["rows"]) == 1 and lone["rows"][0]["me"]
        assert (await client.get("/api/leaderboard?scope=x", headers=hdr(1))).status == 400
        hist = await (await client.get("/api/bets/history", headers=hdr(1))).json()
        assert len(hist["bets"]) == 3 and hist["bets"][0]["pick_name"].startswith("Name")
        print("social ok")

        # --- закрытие ставок после старта квалификации ---
        f1.future = make_race(2, NOW + timedelta(hours=5))
        f1.future["Qualifying"] = sess(NOW - timedelta(minutes=5))
        r = await bet(3, kind="winner", pick="d1", stake=50)
        assert r.status == 409 and (await r.json())["error"] == "closed"
        mk = await (await client.get("/api/markets", headers=hdr(3))).json()
        assert mk["open"] is False
        print("closing ok")
    finally:
        await client.close()

    # --- уведомления ---
    sent = []

    async def send(uid, text, lang):
        sent.append((uid, lang, text))

    db2 = Database(":memory:")
    await db2.upsert_user(10, "Ru", None, "ru")
    await db2.upsert_user(11, "En", None, "en")
    await db2.upsert_user(12, "Muted", None, "en")
    await db2.set_notify(12, False)
    f1b = FakeF1()
    race_dt = NOW + timedelta(hours=26)
    f1b.future = make_race(2, race_dt)
    f1b.future["Qualifying"] = sess(NOW + timedelta(minutes=30))
    f1b.past = make_race(1, NOW - timedelta(hours=5))
    n = Notifier(db2, f1b, send, settle_interval=0)
    await n.tick(NOW)
    texts = {(uid, text) for uid, _, text in sent}
    assert {uid for uid, _ in texts} == {10, 11}, "выключенные уведомления не получают сообщений"
    assert any("Квалификация" in text and "через час" in text for uid, text in texts if uid == 10)
    assert any("Qualifying" in text and "in 1 hour" in text for uid, text in texts if uid == 11)
    assert any("results" in text for uid, text in texts if uid == 11), "итоги свежей гонки"
    count = len(sent)
    await n.tick(NOW + timedelta(seconds=30))
    assert len(sent) == count, "повторов быть не должно"
    await n.tick(f1b.future and parse_dt(f1b.future["Qualifying"]) + timedelta(minutes=1))
    assert any("стартует" in t for _, _, t in sent) and any("starting now" in t for _, _, t in sent)
    # ставка пользователя 10 на прошедшую гонку закрывается и приходит сообщение
    await db2.place_bet(10, "2026", 1, "Test GP 1", "winner", "d2", "", "", 100, 3.0)
    f1b.past = make_race(1, NOW - timedelta(hours=5))
    before = len(sent)
    await n.tick(NOW + timedelta(minutes=45))
    assert len(sent) == before + 1 and "+300" in sent[-1][2], sent[-1]
    print("notifier ok")
    print("ALL OK")


if __name__ == "__main__":
    asyncio.run(main())
