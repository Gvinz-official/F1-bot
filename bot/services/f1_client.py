import asyncio
import time
from datetime import datetime, timedelta, timezone

import httpx

from bot.config import (
    BASE,
    CACHE_TTL_DAY,
    CACHE_TTL_LONG,
    CACHE_TTL_SHORT,
    HTTP_RETRIES,
    HTTP_TIMEOUT,
)
from bot.utils.cache import cached
from bot.utils.dates import parse_dt


def _to_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class F1Client:
    def __init__(self):
        self._client = httpx.AsyncClient(base_url=BASE, timeout=HTTP_TIMEOUT)

    async def close(self):
        await self._client.aclose()

    async def _get(self, path):
        for attempt in range(HTTP_RETRIES):
            is_last = attempt == HTTP_RETRIES - 1
            try:
                r = await self._client.get(path)
            except httpx.TransportError:
                if is_last:
                    raise
            else:
                if r.status_code < 500 and r.status_code != 429:
                    r.raise_for_status()
                    return r.json()["MRData"]
                if is_last:
                    r.raise_for_status()
            await asyncio.sleep(2 ** attempt)

    # ---------- календарь ----------
    @cached(ttl=CACHE_TTL_LONG)
    async def get_schedule(self):
        data = await self._get("/current.json?limit=40")
        return data["RaceTable"]["Races"]

    async def get_next_race(self):
        """Ближайшая гонка по расписанию (гонка считается идущей ещё 3 часа)."""
        now = datetime.now(timezone.utc)
        for race in await self.get_schedule():
            dt = parse_dt(race)
            if dt is None:
                if race.get("date", "") >= now.date().isoformat():
                    return race
            elif dt + timedelta(hours=3) > now:
                return race
        return None

    # ---------- результаты ----------
    @cached(ttl=CACHE_TTL_SHORT)
    async def get_last_results(self):
        data = await self._get("/current/last/results.json")
        races = data["RaceTable"]["Races"]
        if not races:
            return None
        return races[0]

    @cached(ttl=CACHE_TTL_SHORT)
    async def get_race_results(self, season, rnd):
        data = await self._get(f"/{season}/{rnd}/results.json")
        races = data["RaceTable"]["Races"]
        return races[0] if races else None

    @cached(ttl=CACHE_TTL_SHORT)
    async def get_qualifying(self, season, rnd):
        data = await self._get(f"/{season}/{rnd}/qualifying.json")
        races = data["RaceTable"]["Races"]
        return races[0].get("QualifyingResults", []) if races else []

    # ---------- зачёты ----------
    @cached(ttl=CACHE_TTL_SHORT)
    async def get_standings(self):
        data = await self._get("/current/driverStandings.json")
        lists = data["StandingsTable"]["StandingsLists"]
        if not lists:
            return []
        return lists[0]["DriverStandings"]

    @cached(ttl=CACHE_TTL_SHORT)
    async def get_constructor_standings(self):
        data = await self._get("/current/constructorStandings.json")
        lists = data["StandingsTable"]["StandingsLists"]
        if not lists:
            return []
        return lists[0]["ConstructorStandings"]

    @cached(ttl=CACHE_TTL_LONG)
    async def get_season_drivers(self):
        """Список пилотов сезона — запасной вариант, пока нет зачёта."""
        data = await self._get("/current/drivers.json?limit=60")
        return data["DriverTable"]["Drivers"]

    # ---------- карьера ----------
    @cached(ttl=CACHE_TTL_DAY)
    async def get_driver_career(self, driver_id):
        data = await self._get(f"/drivers/{driver_id}/driverStandings.json?limit=100")
        history = []
        for sl in data["StandingsTable"]["StandingsLists"]:
            rows = sl.get("DriverStandings") or []
            if not rows:
                continue
            row = rows[0]
            teams = row.get("Constructors") or [{}]
            history.append({
                "season": sl["season"],
                "pos": _to_int(row.get("position")),
                "points": float(row.get("points", 0)),
                "wins": _to_int(row.get("wins"), 0),
                "team": teams[-1].get("name", ""),
            })
        return _summarize(history)

    @cached(ttl=CACHE_TTL_DAY)
    async def get_constructor_career(self, constructor_id):
        data = await self._get(
            f"/constructors/{constructor_id}/constructorStandings.json?limit=100"
        )
        history = []
        for sl in data["StandingsTable"]["StandingsLists"]:
            rows = sl.get("ConstructorStandings") or []
            if not rows:
                continue
            row = rows[0]
            history.append({
                "season": sl["season"],
                "pos": _to_int(row.get("position")),
                "points": float(row.get("points", 0)),
                "wins": _to_int(row.get("wins"), 0),
                "team": row.get("Constructor", {}).get("name", ""),
            })
        return _summarize(history)


def _summarize(history):
    history.sort(key=lambda h: h["season"])
    positions = [h["pos"] for h in history if h["pos"]]
    return {
        "seasons": len(history),
        "titles": sum(1 for h in history if h["pos"] == 1),
        "wins": sum(h["wins"] for h in history),
        "points": sum(h["points"] for h in history),
        "best": min(positions) if positions else None,
        "first": history[0]["season"] if history else None,
        "history": list(reversed(history[-8:])),
    }


if __name__ == "__main__":

    async def check():
        f1 = F1Client()
        race = await f1.get_next_race()
        print(race["raceName"] if race else "нет гонок")
        last = await f1.get_last_results()
        print(last["raceName"] if last else "нет результатов")
        standings = await f1.get_standings()
        print(len(standings), "пилотов в зачёте")
        constructors = await f1.get_constructor_standings()
        print(len(constructors), "команд в кубке")
        t = time.monotonic()
        await f1.close()

    asyncio.run(check())
