"""Фоновая задача: напоминания о сессиях, расчёт ставок, итоги гонки.

Отправку делает переданная функция send(user_id, text, lang) — так класс не зависит
от aiogram и легко тестируется.
"""
import asyncio
import html
import logging
from datetime import datetime, timedelta, timezone

from bot.config import DEFAULT_TIMEZONE
from bot.i18n import t
from bot.services.game import settle_pending
from bot.utils.dates import format_dt, parse_dt, race_sessions

log = logging.getLogger(__name__)

REMIND_SESSIONS = ("sprint_quali", "sprint", "quali", "race")
TICK_SECONDS = 60
LIVE_WINDOW = timedelta(minutes=10)      # «стартует сейчас» не позже чем через 10 минут
RESULTS_WINDOW = timedelta(hours=48)     # итоги шлём только по свежим гонкам


class Notifier:
    def __init__(self, db, f1, send, settle_interval=1800):
        self.db = db
        self.f1 = f1
        self.send = send
        self.settle_interval = timedelta(seconds=settle_interval)
        self._next_settle = datetime.min.replace(tzinfo=timezone.utc)
        self._startup = True
        self._seen = set()  # метки, уже обработанные в памяти: не дёргаем базу каждую минуту

    async def _first_time(self, marker):
        """True, если метку видим впервые (и записываем её)."""
        if marker in self._seen:
            return False
        self._seen.add(marker)
        if await self.db.was_sent(marker):
            return False
        await self.db.mark_sent(marker)
        return True

    async def run(self):
        while True:
            try:
                await self.tick()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Ошибка в цикле уведомлений")
            await asyncio.sleep(TICK_SECONDS)

    async def tick(self, now=None):
        now = now or datetime.now(timezone.utc)
        await self._reminders(now)
        await self._settle(now)
        await self._results(now)

    # ---------- напоминания ----------
    async def _reminders(self, now):
        race = await self.f1.get_next_race()
        if not race:
            return
        sessions = dict(race_sessions(race))
        for key in REMIND_SESSIONS:
            dt = sessions.get(key)
            if dt is None:
                continue
            for lead in ("1h", "0"):
                if lead == "1h":
                    due = dt - timedelta(hours=1) <= now < dt
                else:
                    due = dt <= now < dt + LIVE_WINDOW
                if not due:
                    continue
                marker = f"{race['season']}:{race['round']}:{key}:{lead}"
                if not await self._first_time(marker):  # отметка до рассылки: не слать дважды
                    continue
                await self._broadcast(self._reminder_text(race, key, dt, lead))

    @staticmethod
    def _reminder_text(race, key, dt, lead):
        def build(lang, tz):
            fields = dict(
                session=t(lang, f"session_{key}"),
                race=html.escape(race["raceName"]),
            )
            if lead == "1h":
                return t(lang, "notif_soon", time=format_dt(dt, tz, lang), tz=tz, **fields)
            return t(lang, "notif_live", **fields)
        return build

    async def _broadcast(self, build):
        for user in await self.db.notify_users():
            tz = user["tz"] or DEFAULT_TIMEZONE
            await self.send(user["id"], build(user["lang"], tz), user["lang"])
            await asyncio.sleep(0.05)  # ~20 сообщений в секунду, лимит Telegram — 30

    # ---------- ставки ----------
    async def _settle(self, now):
        # В базу заглядываем раз в полчаса и только если недавно была гонка
        # (плюс один раз при старте): так бесплатная база успевает засыпать.
        if now < self._next_settle:
            return
        self._next_settle = now + self.settle_interval
        recent = False
        for race in await self.f1.get_schedule():
            dt = parse_dt(race)
            if dt and dt + timedelta(minutes=90) <= now <= dt + timedelta(days=7):
                recent = True
                break
        due, self._startup = self._startup or recent, False
        if not due:
            return
        for bet in await settle_pending(self.db, self.f1, now):
            user = await self.db.get_user(bet["user_id"])
            if not user:
                continue
            lang = user["lang"]
            key = {"won": "bet_won", "lost": "bet_lost", "void": "bet_void"}[bet["status"]]
            text = t(
                lang, key,
                race=html.escape(bet["race_name"]),
                kind=t(lang, f"kind_{bet['kind']}"),
                pick=html.escape(bet["pick_name"]),
                stake=bet["stake"],
                payout=bet["payout"],
            )
            await self.send(user["id"], text, lang)
            await asyncio.sleep(0.05)

    # ---------- итоги гонки ----------
    async def _results(self, now):
        last = await self.f1.get_last_results()
        if not last or not last.get("Results"):
            return
        race_dt = parse_dt(last)
        if race_dt is None or not (race_dt <= now < race_dt + RESULTS_WINDOW):
            return
        marker = f"{last['season']}:{last['round']}:results"
        if not await self._first_time(marker):
            return
        top = [r["Driver"]["familyName"] for r in last["Results"][:3]]
        top += ["—"] * (3 - len(top))

        def build(lang, tz):
            return t(
                lang, "notif_results",
                race=html.escape(last["raceName"]),
                p1=html.escape(top[0]), p2=html.escape(top[1]), p3=html.escape(top[2]),
            )

        await self._broadcast(build)
