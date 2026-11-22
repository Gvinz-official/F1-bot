"""Все тексты бота на двух языках. Использование: t(lang, "key", name=...)."""
from bot.config import DEFAULT_LANG

DIVIDER = "━━━━━━━━━━━━━━━━━━"

TEXTS = {
    "en": {
        "start": (
            "🏎️ <b>WELCOME TO F1 TRACKER!</b> 🏁\n\n"
            "Your Formula 1 companion, right inside Telegram.\n\n"
            "🏆 <b>WHAT'S INSIDE?</b>\n\n"
            "🗓 Season calendar with a live countdown\n"
            "🏁 Race results and championship standings\n"
            "🏎 Driver and team cards with career stats\n"
            "🎮 Mini-games: bet virtual coins on the race, duels, reaction test\n"
            "🔔 Reminders before qualifying and the race\n\n"
            f"{DIVIDER}\n\n"
            "🚦 Tap <b>Open app</b> to start.\n"
            "💡 /help — all commands"
        ),
        "help": (
            "🏎️ <b>F1 TRACKER | COMMAND CENTER</b>\n\n"
            "📡 <b>GENERAL</b>\n\n"
            "🏁 /start — Launch F1 Tracker\n"
            "🎮 /app — Open the mini app\n"
            "📋 /menu — Open the main menu\n"
            "🌐 /lang — Change language\n"
            "🔔 /notify — Turn reminders on/off\n"
            "📖 /help — This message\n"
            "ℹ️ /about — About F1 Tracker\n\n"
            f"{DIVIDER}\n\n"
            "🏆 <b>TRACK THE ACTION</b>\n\n"
            "🗓 /next — Next Grand Prix schedule\n"
            "🏁 /results — Latest race results\n"
            "🏎️ /standings — Driver standings\n"
            "🏗 /constructors — Constructor standings\n"
            "👤 /driver &lt;surname&gt; — Driver card, e.g. /driver norris\n\n"
            f"{DIVIDER}\n\n"
            "🚦 <b>EVERY SECOND COUNTS.</b>"
        ),
        "about": (
            "🏎️ <b>ABOUT F1 TRACKER</b>\n\n"
            f"{DIVIDER}\n\n"
            "F1 Tracker brings Formula 1 to your fingertips: schedule, results, "
            "standings and a mini app with games.\n\n"
            "🪙 Coins in the games are virtual. There is no real money, "
            "no payments and no withdrawals.\n\n"
            f"{DIVIDER}\n\n"
            "<i>Every Lap. Every Second. Every Race.</i>"
        ),
        "menu_title": "🏎 Main menu",
        "btn_next": "🏁 Next race",
        "btn_results": "🏆 Results",
        "btn_standings": "📊 Standings",
        "btn_drivers": "🏎 Drivers",
        "btn_constructors": "🏗 Constructors",
        "btn_back": "⬅ Back",
        "btn_app": "🎮 Open app",
        "standings_choose": "⚡ Choose category:",
        "drivers_title": "🏎 <b>Drivers standings</b>",
        "constructors_title": "🏗 <b>Constructors standings</b>",
        "wins": "wins",
        "waiting_season": "📅 Season is not started yet!",
        "results_empty": "🏁 No race results yet!",
        "next_waiting": "🏁 Waiting for next season!",
        "next_text": (
            "🏁 <b>{race}</b>\n\n"
            "📍 <b>Place:</b> {place}, {country}\n"
            "⏱ <b>Qualifying:</b> {quali} ({tz})\n"
            "🏎 <b>Race:</b> {race_time} ({tz})"
        ),
        "unknown": "Unknown",
        "driver_usage": "Usage: /driver &lt;surname&gt;, for example: /driver norris",
        "driver_not_found": "Driver not found: {query}",
        "driver_many": "Several drivers match, be more specific:",
        "driver_too_long": "We don't have a driver with such a long name",
        "driver_card": (
            "🏎 <b>{name}</b> ({code})\n"
            "Nationality: <b>{nat}</b>\n"
            "Team: <b>{team}</b>\n"
            "Stats:\n  Position — <b>{pos}</b>\n  Wins — <b>{wins}</b>\n  Points — <b>{points}</b>"
        ),
        "lang_choose": "🌐 Choose your language:",
        "lang_set": "✅ Language changed to English.",
        "notify_on": "🔔 Reminders are on. I'll message you before qualifying and the race.",
        "notify_off": "🔕 Reminders are off.",
        "app_open": "🎮 Open the F1 mini app:",
        "app_unavailable": "The mini app isn't configured yet. Set WEBAPP_URL in .env.",
        "ref_joined": "🤝 You and <b>{name}</b> are now friends! +{coins} 🪙 each.",
        "session_fp1": "Practice 1",
        "session_fp2": "Practice 2",
        "session_fp3": "Practice 3",
        "session_sprint_quali": "Sprint Qualifying",
        "session_sprint": "Sprint",
        "session_quali": "Qualifying",
        "session_race": "Race",
        "notif_soon": "⏰ <b>{session}</b> starts in 1 hour!\n🏁 {race}\n🕒 {time} ({tz})",
        "notif_live": "🚦 <b>{session}</b> is starting now!\n🏁 {race}",
        "notif_results": "🏁 <b>{race}</b> — results are in!\n\n🥇 {p1}\n🥈 {p2}\n🥉 {p3}",
        "kind_winner": "winner",
        "kind_podium": "podium",
        "kind_pole": "pole",
        "kind_h2h": "duel",
        "bet_won": "✅ <b>{race}</b>: your {kind} bet on {pick} won! +{payout} 🪙",
        "bet_lost": "❌ <b>{race}</b>: your {kind} bet on {pick} didn't win. −{stake} 🪙",
        "bet_void": "↩️ <b>{race}</b>: your {kind} bet on {pick} was refunded (+{stake} 🪙).",
    },
    "ru": {
        "start": (
            "🏎️ <b>ДОБРО ПОЖАЛОВАТЬ В F1 TRACKER!</b> 🏁\n\n"
            "Ваш помощник по Формуле 1 прямо в Telegram.\n\n"
            "🏆 <b>ЧТО ВНУТРИ?</b>\n\n"
            "🗓 Календарь сезона с живым отсчётом до гонки\n"
            "🏁 Результаты гонок и чемпионские таблицы\n"
            "🏎 Карточки пилотов и команд со статистикой\n"
            "🎮 Мини-игры: ставки виртуальными монетами, дуэли, тест реакции\n"
            "🔔 Напоминания перед квалификацией и гонкой\n\n"
            f"{DIVIDER}\n\n"
            "🚦 Нажмите <b>Открыть приложение</b>, чтобы начать.\n"
            "💡 /help — все команды"
        ),
        "help": (
            "🏎️ <b>F1 TRACKER | ЦЕНТР КОМАНД</b>\n\n"
            "📡 <b>ОБЩЕЕ</b>\n\n"
            "🏁 /start — Запустить F1 Tracker\n"
            "🎮 /app — Открыть мини-приложение\n"
            "📋 /menu — Главное меню\n"
            "🌐 /lang — Сменить язык\n"
            "🔔 /notify — Включить/выключить напоминания\n"
            "📖 /help — Это сообщение\n"
            "ℹ️ /about — О боте\n\n"
            f"{DIVIDER}\n\n"
            "🏆 <b>СЛЕДИТЕ ЗА ГОНКАМИ</b>\n\n"
            "🗓 /next — Расписание следующего Гран-при\n"
            "🏁 /results — Результаты последней гонки\n"
            "🏎️ /standings — Личный зачёт\n"
            "🏗 /constructors — Кубок конструкторов\n"
            "👤 /driver &lt;фамилия&gt; — Карточка пилота, например /driver norris\n\n"
            f"{DIVIDER}\n\n"
            "🚦 <b>КАЖДАЯ СЕКУНДА ВАЖНА.</b>"
        ),
        "about": (
            "🏎️ <b>О F1 TRACKER</b>\n\n"
            f"{DIVIDER}\n\n"
            "F1 Tracker приносит Формулу 1 в ваш Telegram: расписание, результаты, "
            "таблицы и мини-приложение с играми.\n\n"
            "🪙 Монеты в играх виртуальные. Реальных денег, платежей и вывода "
            "средств нет.\n\n"
            f"{DIVIDER}\n\n"
            "<i>Every Lap. Every Second. Every Race.</i>"
        ),
        "menu_title": "🏎 Главное меню",
        "btn_next": "🏁 Следующая гонка",
        "btn_results": "🏆 Результаты",
        "btn_standings": "📊 Таблицы",
        "btn_drivers": "🏎 Пилоты",
        "btn_constructors": "🏗 Команды",
        "btn_back": "⬅ Назад",
        "btn_app": "🎮 Открыть приложение",
        "standings_choose": "⚡ Выберите категорию:",
        "drivers_title": "🏎 <b>Личный зачёт</b>",
        "constructors_title": "🏗 <b>Кубок конструкторов</b>",
        "wins": "поб.",
        "waiting_season": "📅 Сезон ещё не начался!",
        "results_empty": "🏁 Результатов гонок пока нет!",
        "next_waiting": "🏁 Ждём следующий сезон!",
        "next_text": (
            "🏁 <b>{race}</b>\n\n"
            "📍 <b>Место:</b> {place}, {country}\n"
            "⏱ <b>Квалификация:</b> {quali} ({tz})\n"
            "🏎 <b>Гонка:</b> {race_time} ({tz})"
        ),
        "unknown": "Неизвестно",
        "driver_usage": "Использование: /driver &lt;фамилия&gt;, например: /driver norris",
        "driver_not_found": "Пилот не найден: {query}",
        "driver_many": "Подходит несколько пилотов, уточните запрос:",
        "driver_too_long": "У нас нет пилота с такой длинной фамилией",
        "driver_card": (
            "🏎 <b>{name}</b> ({code})\n"
            "Страна: <b>{nat}</b>\n"
            "Команда: <b>{team}</b>\n"
            "Статистика:\n  Позиция — <b>{pos}</b>\n  Победы — <b>{wins}</b>\n  Очки — <b>{points}</b>"
        ),
        "lang_choose": "🌐 Выберите язык:",
        "lang_set": "✅ Язык изменён на русский.",
        "notify_on": "🔔 Напоминания включены. Напишу перед квалификацией и гонкой.",
        "notify_off": "🔕 Напоминания выключены.",
        "app_open": "🎮 Открыть мини-приложение F1:",
        "app_unavailable": "Мини-приложение ещё не настроено. Укажите WEBAPP_URL в .env.",
        "ref_joined": "🤝 Теперь вы с <b>{name}</b> друзья! +{coins} 🪙 каждому.",
        "session_fp1": "Практика 1",
        "session_fp2": "Практика 2",
        "session_fp3": "Практика 3",
        "session_sprint_quali": "Квалификация к спринту",
        "session_sprint": "Спринт",
        "session_quali": "Квалификация",
        "session_race": "Гонка",
        "notif_soon": "⏰ <b>{session}</b> начнётся через час!\n🏁 {race}\n🕒 {time} ({tz})",
        "notif_live": "🚦 <b>{session}</b> стартует прямо сейчас!\n🏁 {race}",
        "notif_results": "🏁 <b>{race}</b> — результаты готовы!\n\n🥇 {p1}\n🥈 {p2}\n🥉 {p3}",
        "kind_winner": "победитель",
        "kind_podium": "подиум",
        "kind_pole": "поул",
        "kind_h2h": "дуэль",
        "bet_won": "✅ <b>{race}</b>: ставка ({kind}) на {pick} сыграла! +{payout} 🪙",
        "bet_lost": "❌ <b>{race}</b>: ставка ({kind}) на {pick} не сыграла. −{stake} 🪙",
        "bet_void": "↩️ <b>{race}</b>: ставка ({kind}) на {pick} возвращена (+{stake} 🪙).",
    },
}


def t(lang, key, **kwargs):
    table = TEXTS.get(lang) or TEXTS[DEFAULT_LANG]
    text = table.get(key)
    if text is None:
        text = TEXTS[DEFAULT_LANG][key]
    return text.format(**kwargs) if kwargs else text
