"""Виртуальные ставки: коэффициенты считаются по очкам в чемпионате."""
import logging
import math
from datetime import datetime, timedelta, timezone

from bot.services.models import driver_info, norm_standing
from bot.utils.dates import parse_dt

log = logging.getLogger(__name__)

KINDS = ("winner", "podium", "pole", "h2h")
MARGIN = 0.88  # «маржа букмекера»: чем ниже, тем скромнее коэффициенты


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _weight(points):
    return (float(points) + 10.0) ** 1.5


def drivers_for_markets(standings, season_drivers):
    """Пилоты для рынков: из зачёта, а до первой гонки — из списка сезона."""
    if standings:
        return [norm_standing(r) for r in standings]
    out = []
    for d in season_drivers:
        info = driver_info(d)
        info.update({"pos": None, "team": "", "team_id": "", "points": 0, "wins": 0})
        out.append(info)
    return out


def build_markets(drivers):
    """-> {'winner': [...], 'podium': [...], 'pole': [...], 'h2h': [...]}"""
    if not drivers:
        return {"winner": [], "podium": [], "pole": [], "h2h": []}
    weights = {d["id"]: _weight(d["points"]) for d in drivers}
    total = sum(weights.values())

    def entry(d, odds):
        return {
            "id": d["id"], "code": d["code"], "name": d["name"], "number": d.get("number"),
            "team": d["team"], "team_id": d["team_id"], "odds": round(odds, 2),
        }

    winner, podium, pole = [], [], []
    for d in drivers:
        p = weights[d["id"]] / total
        winner.append(entry(d, _clamp(MARGIN / p, 1.1, 99)))
        podium.append(entry(d, _clamp(MARGIN / (1 - (1 - p) ** 3.2), 1.05, 60)))
        pole.append(entry(d, _clamp((MARGIN - 0.02) / p, 1.1, 99)))

    h2h = []
    teams = {}
    for d in drivers:
        if d["team_id"]:
            teams.setdefault(d["team_id"], []).append(d)
    for team_id, members in teams.items():
        if len(members) < 2:
            continue
        a, b = sorted(members, key=lambda d: -d["points"])[:2]
        pa = weights[a["id"]] / (weights[a["id"]] + weights[b["id"]])
        h2h.append({
            "team_id": team_id,
            "team": a["team"],
            "a": entry(a, _clamp(0.92 / pa, 1.05, 20)),
            "b": entry(b, _clamp(0.92 / (1 - pa), 1.05, 20)),
        })
    h2h.sort(key=lambda m: m["a"]["odds"] + m["b"]["odds"])
    return {"winner": winner, "podium": podium, "pole": pole, "h2h": h2h}


def find_selection(markets, kind, pick, ref=""):
    """-> (odds, opponent_id, ref) или None, если такого выбора нет."""
    if kind in ("winner", "podium", "pole"):
        for e in markets.get(kind, []):
            if e["id"] == pick:
                return e["odds"], "", ""
        return None
    if kind == "h2h":
        for m in markets.get("h2h", []):
            if m["team_id"] != ref:
                continue
            if pick == m["a"]["id"]:
                return m["a"]["odds"], m["b"]["id"], ref
            if pick == m["b"]["id"]:
                return m["b"]["odds"], m["a"]["id"], ref
    return None


def betting_closes_at(race):
    """Ставки закрываются со стартом квалификации (или гонки, если квалы нет)."""
    return parse_dt(race.get("Qualifying")) or parse_dt(race)


def is_betting_open(race, now=None):
    closes = betting_closes_at(race)
    now = now or datetime.now(timezone.utc)
    return closes is not None and now < closes


# ---------- расчёт ----------
def evaluate(bet, results, quali):
    """-> ('won' | 'lost' | 'void')"""
    rows = results.get("Results", [])
    order = {}
    for r in rows:
        pos = str(r.get("position", ""))
        if pos.isdigit():
            order[r["Driver"]["driverId"]] = int(pos)

    kind, pick = bet["kind"], bet["pick"]
    if kind == "winner":
        return "won" if order.get(pick) == 1 else "lost"
    if kind == "podium":
        return "won" if order.get(pick, 99) <= 3 else "lost"
    if kind == "pole":
        pole_id = None
        for q in quali or []:
            if str(q.get("position")) == "1":
                pole_id = q["Driver"]["driverId"]
                break
        if pole_id is None:  # запасной вариант: стартовая решётка
            for r in rows:
                if str(r.get("grid")) == "1":
                    pole_id = r["Driver"]["driverId"]
                    break
        if pole_id is None:
            return "void"
        return "won" if pole_id == pick else "lost"
    if kind == "h2h":
        mine, other = order.get(pick), order.get(bet["opponent"])
        if mine is None or other is None:
            return "void"
        return "won" if mine < other else "lost"
    return "void"


def payout_for(bet, status):
    if status == "won":
        return int(math.floor(bet["stake"] * bet["odds"]))
    if status == "void":
        return bet["stake"]
    return 0


async def settle_pending(db, f1, now=None):
    """Закрывает ставки по завершённым гонкам. -> список итогов для уведомлений."""
    now = now or datetime.now(timezone.utc)
    settled = []
    rounds = await db.open_rounds()
    if not rounds:
        return settled
    schedule = {(r["season"], int(r["round"])): r for r in await f1.get_schedule()}
    for item in rounds:
        season, rnd = item["season"], item["round"]
        race = schedule.get((season, rnd))
        race_dt = parse_dt(race) if race else None
        if race_dt and now < race_dt + timedelta(minutes=90):
            continue  # гонка ещё не могла закончиться
        try:
            results = await f1.get_race_results(season, rnd)
            if not results or not results.get("Results"):
                continue
            quali = await f1.get_qualifying(season, rnd)
        except Exception:
            log.exception("Не удалось получить результаты %s/%s", season, rnd)
            continue
        by_id = {r["Driver"]["driverId"]: r["Driver"]["familyName"] for r in results["Results"]}
        for bet in await db.open_bets(season, rnd):
            status = evaluate(bet, results, quali)
            payout = payout_for(bet, status)
            if await db.settle_bet(bet["id"], status, payout):
                bet = dict(bet, status=status, payout=payout)
                bet["pick_name"] = by_id.get(bet["pick"], bet["pick"])
                settled.append(bet)
    return settled
