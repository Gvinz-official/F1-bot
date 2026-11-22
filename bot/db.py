"""Хранилище: SQLite локально, Postgres (Neon и т.п.), если задан DATABASE_URL.

Вся логика одна на оба движка: _Store работает через маленький адаптер _Tx.
Бот запускается одним процессом, поэтому последовательность операций
гарантирует замок threading.RLock (отдельные блокировки строк не нужны).
"""
import asyncio
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone

from bot.config import DAILY_BONUS, DAILY_STREAK_STEP, DEFAULT_LANG, START_COINS

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users(
        id BIGINT PRIMARY KEY,
        name TEXT NOT NULL DEFAULT '',
        username TEXT,
        lang TEXT NOT NULL DEFAULT 'en',
        tz TEXT,
        notify INTEGER NOT NULL DEFAULT 1,
        coins BIGINT NOT NULL DEFAULT 1000,
        last_daily TEXT,
        streak INTEGER NOT NULL DEFAULT 0,
        best_reaction INTEGER,
        created_at TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS friends(
        a BIGINT NOT NULL, b BIGINT NOT NULL, PRIMARY KEY(a, b))""",
    """CREATE TABLE IF NOT EXISTS bets(
        id {BIGID},
        user_id BIGINT NOT NULL,
        season TEXT NOT NULL,
        round INTEGER NOT NULL,
        race_name TEXT NOT NULL DEFAULT '',
        kind TEXT NOT NULL,
        pick TEXT NOT NULL,
        ref TEXT NOT NULL DEFAULT '',
        opponent TEXT NOT NULL DEFAULT '',
        stake INTEGER NOT NULL,
        odds DOUBLE PRECISION NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        payout INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        UNIQUE(user_id, season, round, kind, ref))""",
    "CREATE INDEX IF NOT EXISTS idx_bets_open ON bets(status, season, round)",
    "CREATE TABLE IF NOT EXISTS sent(key TEXT PRIMARY KEY)",
    """CREATE TABLE IF NOT EXISTS reaction_plays(
        user_id BIGINT NOT NULL, day TEXT NOT NULL, plays INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(user_id, day))""",
]

RU_LIKE = {"ru", "uk", "be", "uz", "kk", "ky", "tg", "hy", "az"}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today():
    return datetime.now(timezone.utc).date().isoformat()


class _Abort(Exception):
    """Откат транзакции с кодом результата."""

    def __init__(self, code):
        self.code = code


class _Tx:
    """Единый интерфейс запросов: ? в SQL превращается в %s для Postgres."""

    def __init__(self, conn, pg):
        self.conn, self.pg = conn, pg

    def _exec(self, sql, args):
        return self.conn.execute(sql.replace("?", "%s") if self.pg else sql, tuple(args))

    def run(self, sql, args=()):
        return self._exec(sql, args).rowcount

    def one(self, sql, args=()):
        row = self._exec(sql, args).fetchone()
        return dict(row) if row else None

    def all(self, sql, args=()):
        return [dict(r) for r in self._exec(sql, args).fetchall()]


class _Sqlite:
    def __init__(self, path):
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        for stmt in SCHEMA:
            self.conn.execute(stmt.replace("{BIGID}", "INTEGER PRIMARY KEY AUTOINCREMENT"))
        self.conn.commit()

    @contextmanager
    def tx(self):
        with self.lock, self.conn:
            yield _Tx(self.conn, False)

    def close(self):
        with self.lock:
            self.conn.close()


class _Postgres:
    def __init__(self, url):
        from psycopg.rows import dict_row
        from psycopg_pool import ConnectionPool

        self.lock = threading.RLock()
        # min_size=0 и max_idle: не держим соединения открытыми, чтобы бесплатная
        # база могла засыпать; prepare_threshold=None нужен для пулера (PgBouncer).
        self.pool = ConnectionPool(
            url, min_size=0, max_size=4, max_idle=120, timeout=30, open=True,
            kwargs={"row_factory": dict_row, "prepare_threshold": None},
            check=ConnectionPool.check_connection,
        )
        with self.tx() as c:
            for stmt in SCHEMA:
                c.run(stmt.replace("{BIGID}", "BIGSERIAL PRIMARY KEY"))

    @contextmanager
    def tx(self):
        with self.lock, self.pool.connection() as conn:
            yield _Tx(conn, True)

    def close(self):
        self.pool.close()


def _backend(target):
    if str(target).startswith(("postgres://", "postgresql://")):
        return _Postgres(target)
    return _Sqlite(target)


class _Store:
    def __init__(self, target):
        self._db = _backend(target)

    def close(self):
        self._db.close()

    # ---------- users ----------
    def upsert_user(self, user_id, name, username, language_code):
        name = (name or "").strip()[:64] or "Racer"
        with self._db.tx() as c:
            row = c.one("SELECT * FROM users WHERE id=?", (user_id,))
            if row is None:
                lang = "ru" if (language_code or "").split("-")[0] in RU_LIKE else DEFAULT_LANG
                c.run(
                    "INSERT INTO users(id,name,username,lang,coins,created_at) VALUES(?,?,?,?,?,?) "
                    "ON CONFLICT DO NOTHING",
                    (user_id, name, username, lang, START_COINS, _now()),
                )
            elif row["name"] != name or row["username"] != username:
                c.run("UPDATE users SET name=?, username=? WHERE id=?", (name, username, user_id))
            return c.one("SELECT * FROM users WHERE id=?", (user_id,))

    def get_user(self, user_id):
        with self._db.tx() as c:
            return c.one("SELECT * FROM users WHERE id=?", (user_id,))

    def set_lang(self, user_id, lang):
        with self._db.tx() as c:
            c.run("UPDATE users SET lang=? WHERE id=?", (lang, user_id))

    def set_tz(self, user_id, tz):
        with self._db.tx() as c:
            c.run("UPDATE users SET tz=? WHERE id=?", (tz, user_id))

    def set_notify(self, user_id, value):
        with self._db.tx() as c:
            c.run("UPDATE users SET notify=? WHERE id=?", (1 if value else 0, user_id))

    def notify_users(self):
        with self._db.tx() as c:
            return c.all("SELECT id, lang, tz FROM users WHERE notify=1")

    def add_coins(self, user_id, delta):
        with self._db.tx() as c:
            c.run("UPDATE users SET coins = coins + ? WHERE id=?", (delta, user_id))
            return c.one("SELECT coins FROM users WHERE id=?", (user_id,))["coins"]

    # ---------- daily bonus ----------
    def claim_daily(self, user_id, today=None):
        today = today or _today()
        with self._db.tx() as c:
            u = c.one("SELECT * FROM users WHERE id=?", (user_id,))
            if u is None or u["last_daily"] == today:
                return None
            yesterday = (date.fromisoformat(today) - timedelta(days=1)).isoformat()
            streak = u["streak"] + 1 if u["last_daily"] == yesterday else 1
            bonus = DAILY_BONUS + min(streak - 1, 6) * DAILY_STREAK_STEP
            c.run(
                "UPDATE users SET coins=coins+?, streak=?, last_daily=? WHERE id=?",
                (bonus, streak, today, user_id),
            )
            coins = c.one("SELECT coins FROM users WHERE id=?", (user_id,))["coins"]
            return {"bonus": bonus, "streak": streak, "coins": coins}

    # ---------- friends ----------
    def add_friends(self, a, b):
        """True, если дружба новая."""
        if a == b:
            return False
        with self._db.tx() as c:
            if c.one("SELECT 1 AS x FROM friends WHERE a=? AND b=?", (a, b)):
                return False
            c.run("INSERT INTO friends(a,b) VALUES(?,?) ON CONFLICT DO NOTHING", (a, b))
            c.run("INSERT INTO friends(a,b) VALUES(?,?) ON CONFLICT DO NOTHING", (b, a))
            return True

    def friend_ids(self, user_id):
        with self._db.tx() as c:
            return [r["b"] for r in c.all("SELECT b FROM friends WHERE a=?", (user_id,))]

    # ---------- bets ----------
    def place_bet(self, user_id, season, rnd, race_name, kind, pick, ref, opponent, stake, odds):
        """-> ('ok', coins_left) | ('no_funds', None) | ('duplicate', None)"""
        try:
            with self._db.tx() as c:
                n = c.run(
                    "INSERT INTO bets(user_id,season,round,race_name,kind,pick,ref,opponent,"
                    "stake,odds,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING",
                    (user_id, str(season), int(rnd), race_name, kind, pick, ref, opponent,
                     stake, odds, _now()),
                )
                if n != 1:
                    raise _Abort("duplicate")
                n = c.run(
                    "UPDATE users SET coins=coins-? WHERE id=? AND coins>=?", (stake, user_id, stake)
                )
                if n != 1:
                    raise _Abort("no_funds")  # откат: ставка не сохранится
                return "ok", c.one("SELECT coins FROM users WHERE id=?", (user_id,))["coins"]
        except _Abort as e:
            return e.code, None

    def user_bets(self, user_id, limit=40, season=None, rnd=None):
        with self._db.tx() as c:
            if season is not None:
                return c.all(
                    "SELECT * FROM bets WHERE user_id=? AND season=? AND round=? ORDER BY id DESC",
                    (user_id, str(season), int(rnd)),
                )
            return c.all("SELECT * FROM bets WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))

    def open_rounds(self):
        with self._db.tx() as c:
            return c.all(
                "SELECT DISTINCT season, round FROM bets WHERE status='open' ORDER BY season, round"
            )

    def open_bets(self, season, rnd):
        with self._db.tx() as c:
            return c.all(
                "SELECT * FROM bets WHERE status='open' AND season=? AND round=?",
                (str(season), int(rnd)),
            )

    def settle_bet(self, bet_id, status, payout):
        """Идемпотентно: True только при первом закрытии ставки."""
        with self._db.tx() as c:
            if c.run(
                "UPDATE bets SET status=?, payout=? WHERE id=? AND status='open'",
                (status, payout, bet_id),
            ) != 1:
                return False
            if payout:
                uid = c.one("SELECT user_id FROM bets WHERE id=?", (bet_id,))["user_id"]
                c.run("UPDATE users SET coins=coins+? WHERE id=?", (payout, uid))
            return True

    # ---------- уведомления ----------
    def was_sent(self, key):
        with self._db.tx() as c:
            return c.one("SELECT 1 AS x FROM sent WHERE key=?", (key,)) is not None

    def mark_sent(self, key):
        with self._db.tx() as c:
            c.run("INSERT INTO sent(key) VALUES(?) ON CONFLICT DO NOTHING", (key,))

    # ---------- реакция ----------
    def record_reaction(self, user_id, ms, reward, cap, day=None):
        day = day or _today()
        with self._db.tx() as c:
            row = c.one("SELECT plays FROM reaction_plays WHERE user_id=? AND day=?", (user_id, day))
            plays = row["plays"] if row else 0
            rewarded = plays < cap
            if rewarded:
                c.run(
                    "INSERT INTO reaction_plays(user_id,day,plays) VALUES(?,?,1) "
                    "ON CONFLICT(user_id,day) DO UPDATE SET plays=reaction_plays.plays+1",
                    (user_id, day),
                )
                plays += 1
                c.run("UPDATE users SET coins=coins+? WHERE id=?", (reward, user_id))
            c.run(
                "UPDATE users SET best_reaction=? WHERE id=? AND (best_reaction IS NULL OR best_reaction>?)",
                (ms, user_id, ms),
            )
            u = c.one("SELECT coins, best_reaction FROM users WHERE id=?", (user_id,))
            return {
                "rewarded": rewarded,
                "reward": reward if rewarded else 0,
                "coins": u["coins"],
                "best": u["best_reaction"],
                "plays_left": max(cap - plays, 0),
            }

    def reaction_plays_left(self, user_id, cap, day=None):
        day = day or _today()
        with self._db.tx() as c:
            row = c.one("SELECT plays FROM reaction_plays WHERE user_id=? AND day=?", (user_id, day))
            return max(cap - (row["plays"] if row else 0), 0)

    # ---------- рейтинги ----------
    def leaderboard(self, board, ids=None, limit=20):
        col, order, cond = (
            ("coins", "DESC", "1=1") if board == "coins"
            else ("best_reaction", "ASC", "best_reaction IS NOT NULL")
        )
        sql = f"SELECT id, name, username, {col} AS value FROM users WHERE {cond}"
        args = []
        if ids is not None:
            if not ids:
                return []
            sql += f" AND id IN ({','.join('?' * len(ids))})"
            args += list(ids)
        sql += f" ORDER BY {col} {order}, id LIMIT ?"
        args.append(limit)
        with self._db.tx() as c:
            rows = c.all(sql, args)
        for i, r in enumerate(rows, 1):
            r["rank"] = i
        return rows

    def user_rank(self, user_id, board, ids=None):
        """Место пользователя в рейтинге (или None, если его там нет)."""
        with self._db.tx() as c:
            u = c.one("SELECT coins, best_reaction FROM users WHERE id=?", (user_id,))
            if u is None:
                return None
            if board == "coins":
                value, cmp, cond, col = u["coins"], ">", "1=1", "coins"
            else:
                if u["best_reaction"] is None:
                    return None
                value, cmp, cond, col = u["best_reaction"], "<", "best_reaction IS NOT NULL", "best_reaction"
            sql = f"SELECT COUNT(*) AS n FROM users WHERE {cond} AND {col} {cmp} ?"
            args = [value]
            if ids is not None:
                sql += f" AND id IN ({','.join('?' * len(ids))})"
                args += list(ids)
            return c.one(sql, args)["n"] + 1


class Database:
    """Async-обёртка: await db.get_user(1) выполняется в потоке."""

    def __init__(self, target):
        self._store = _Store(target)

    def __getattr__(self, name):
        attr = getattr(self._store, name)
        if not callable(attr):
            return attr

        async def runner(*args, **kwargs):
            return await asyncio.to_thread(attr, *args, **kwargs)

        return runner
