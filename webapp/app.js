"use strict";

const tg = window.Telegram && window.Telegram.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
  try { if (tg.disableVerticalSwipes) tg.disableVerticalSwipes(); } catch (e) { /* старые клиенты */ }
}

/* ======================= тексты ======================= */
const I18N = {
  en: {
    tab_race: "Race", tab_cal: "Calendar", tab_grid: "Standings", tab_play: "Play", tab_me: "Profile",
    round: "Round {n}", d: "d", h: "h", m: "m", s: "s",
    until_race: "until the race", race_live: "Race in progress", lights_out: "Lights out. Follow it live on TV.",
    season_over: "Season complete", season_over_sub: "The new calendar appears once the next season is announced.",
    weekend: "Weekend schedule", next: "Next", last_race: "Last race", all_results: "Full results",
    no_results: "No race results yet.",
    drivers: "Drivers", teams: "Teams", wins: "Wins", points: "Points", position: "Position",
    seasons: "Seasons", titles: "Titles", best_finish: "Best finish", recent: "Recent seasons",
    no_standings: "Standings appear after the first race.",
    s_fp1: "Practice 1", s_fp2: "Practice 2", s_fp3: "Practice 3", s_sprint_quali: "Sprint Qualifying",
    s_sprint: "Sprint", s_quali: "Qualifying", s_race: "Race",
    bets: "Bets", duels: "Duels", start: "Start", top: "Top",
    coins: "Coins", virtual_note: "Coins are virtual. There is no real money, no payments and no withdrawals.",
    closes_in: "Bets close in {t}", closed: "Betting is closed until the next race.",
    no_race_bets: "No upcoming race to bet on.",
    k_winner: "Winner", k_podium: "Podium", k_pole: "Pole", k_h2h: "Duel",
    k_winner_hint: "Who wins the race?", k_podium_hint: "Who finishes in the top three?", k_pole_hint: "Who takes pole position?",
    duel_hint: "Which teammate finishes ahead? Both must be classified, otherwise the stake is refunded.",
    your_bets: "Your bets this weekend", history: "Bet history", no_bets: "No bets yet.",
    st_open: "In play", st_won: "Won", st_lost: "Lost", st_void: "Refunded",
    stake: "Stake", payout: "Possible payout", place_bet: "Place bet", odds: "Odds",
    already_bet: "You already have a {k} bet for this race.",
    low_coins: "Not enough coins. Claim your daily bonus in Profile.",
    bet_placed: "Bet placed", bet_closed: "Betting just closed", bet_dup: "You already placed this bet",
    bet_funds: "Not enough coins", bet_bad: "This selection is no longer available",
    vs: "vs", pick: "Pick",
    react_title: "Lights out", react_intro: "Five lights come on, then go out. Tap as fast as you can after they go out.",
    react_start: "Start the lights", react_wait: "Wait for the lights to go out", react_tap: "Tap now",
    react_false: "False start. Wait until all lights are out.", react_best: "Best: {n} ms", react_runs: "Paid runs left today: {n}",
    react_reward: "+{n} coins", react_no_reward: "No more coins today. Come back tomorrow.",
    react_invalid: "That run could not be verified. Try again.",
    scope_global: "Everyone", scope_friends: "Friends", board_coins: "Coins", board_reaction: "Reaction",
    invite: "Invite friends", invite_text: "Join me in F1 Tracker: race calendar, standings and games.",
    invite_sub: "You both get {n} coins when a friend joins.", no_rank: "No results yet.",
    your_rank: "Your place: {n}",
    profile: "Profile", daily: "Daily bonus", daily_claim: "Claim bonus", daily_done: "Come back tomorrow",
    daily_got: "+{n} coins, streak {s}", streak: "Streak: {n}",
    language: "Language", notifications: "Reminders", notifications_sub: "Before qualifying and the race",
    friends: "Friends: {n}", loading_err: "Something went wrong.",
    err_unauthorized: "Open this app from the Telegram bot.", err_upstream: "F1 data is temporarily unavailable.",
    retry: "Try again", close: "Close", saved: "Saved",
  },
  ru: {
    tab_race: "Гонка", tab_cal: "Календарь", tab_grid: "Зачёт", tab_play: "Игры", tab_me: "Профиль",
    round: "Этап {n}", d: "д", h: "ч", m: "м", s: "с",
    until_race: "до старта гонки", race_live: "Гонка идёт", lights_out: "Огни погасли. Смотрите трансляцию.",
    season_over: "Сезон завершён", season_over_sub: "Новый календарь появится, когда объявят следующий сезон.",
    weekend: "Расписание уикенда", next: "Дальше", last_race: "Последняя гонка", all_results: "Полные результаты",
    no_results: "Результатов гонок пока нет.",
    drivers: "Пилоты", teams: "Команды", wins: "Победы", points: "Очки", position: "Позиция",
    seasons: "Сезонов", titles: "Титулов", best_finish: "Лучшее место", recent: "Последние сезоны",
    no_standings: "Зачёт появится после первой гонки.",
    s_fp1: "Практика 1", s_fp2: "Практика 2", s_fp3: "Практика 3", s_sprint_quali: "Квалификация к спринту",
    s_sprint: "Спринт", s_quali: "Квалификация", s_race: "Гонка",
    bets: "Ставки", duels: "Дуэли", start: "Старт", top: "Топ",
    coins: "Монеты", virtual_note: "Монеты виртуальные. Реальных денег, платежей и вывода средств нет.",
    closes_in: "Ставки закроются через {t}", closed: "Приём ставок закрыт до следующей гонки.",
    no_race_bets: "Нет ближайшей гонки для ставок.",
    k_winner: "Победитель", k_podium: "Подиум", k_pole: "Поул", k_h2h: "Дуэль",
    k_winner_hint: "Кто выиграет гонку?", k_podium_hint: "Кто попадёт в тройку?", k_pole_hint: "Кто возьмёт поул?",
    duel_hint: "Кто из напарников финиширует выше? Оба должны быть классифицированы, иначе ставка вернётся.",
    your_bets: "Ваши ставки на этот уикенд", history: "История ставок", no_bets: "Ставок пока нет.",
    st_open: "В игре", st_won: "Выиграла", st_lost: "Проиграла", st_void: "Возврат",
    stake: "Ставка", payout: "Возможный выигрыш", place_bet: "Сделать ставку", odds: "Коэффициент",
    already_bet: "На эту гонку у вас уже есть ставка: {k}.",
    low_coins: "Не хватает монет. Заберите ежедневный бонус в профиле.",
    bet_placed: "Ставка принята", bet_closed: "Приём ставок только что закрылся", bet_dup: "Такая ставка уже сделана",
    bet_funds: "Не хватает монет", bet_bad: "Этот вариант больше недоступен",
    vs: "против", pick: "Выбор",
    react_title: "Огни погасли", react_intro: "Загорятся пять огней, потом погаснут. Нажмите как можно быстрее после погасания.",
    react_start: "Включить огни", react_wait: "Ждите, пока огни погаснут", react_tap: "Жмите",
    react_false: "Фальстарт. Дождитесь, когда погаснут все огни.", react_best: "Лучший: {n} мс", react_runs: "Оплачиваемых попыток сегодня: {n}",
    react_reward: "+{n} монет", react_no_reward: "Монеты на сегодня закончились. Приходите завтра.",
    react_invalid: "Заезд не удалось проверить. Попробуйте ещё раз.",
    scope_global: "Все", scope_friends: "Друзья", board_coins: "Монеты", board_reaction: "Реакция",
    invite: "Пригласить друзей", invite_text: "Заходи в F1 Tracker: календарь гонок, зачёт и игры.",
    invite_sub: "Когда друг присоединится, вы оба получите по {n} монет.", no_rank: "Пока нет результатов.",
    your_rank: "Ваше место: {n}",
    profile: "Профиль", daily: "Ежедневный бонус", daily_claim: "Забрать бонус", daily_done: "Приходите завтра",
    daily_got: "+{n} монет, серия {s}", streak: "Серия: {n}",
    language: "Язык", notifications: "Напоминания", notifications_sub: "Перед квалификацией и гонкой",
    friends: "Друзей: {n}", loading_err: "Что-то пошло не так.",
    err_unauthorized: "Откройте приложение из Telegram-бота.", err_upstream: "Данные F1 временно недоступны.",
    retry: "Повторить", close: "Закрыть", saved: "Сохранено",
  },
};

const S = {
  me: null, lang: "en", tab: "race", gridTab: "drivers", playTab: "bets", market: "winner",
  scope: "global", board: "coins", cache: new Map(), renderId: 0, gantryPlayed: false,
  drivers: new Map(), teams: new Map(), stake: null, react: null, lastFire: 0,
};

const t = (key, vars) => {
  let s = (I18N[S.lang] && I18N[S.lang][key]) || I18N.en[key] || key;
  if (vars) for (const k in vars) s = s.replace("{" + k + "}", () => vars[k]);
  return s;
};
const esc = (v) => String(v == null ? "" : v).replace(/[&<>"']/g, (c) => (
  { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const $ = (sel, root) => (root || document).querySelector(sel);
const fmt = (n) => Number(n).toLocaleString(S.lang === "ru" ? "ru-RU" : "en-US");
const locale = () => (S.lang === "ru" ? "ru-RU" : "en-GB");
const userTz = () => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (e) { return ""; } };

/* ======================= цвета команд ======================= */
const TEAM_COLORS = {
  red_bull: "#3671c6", ferrari: "#e8002d", mercedes: "#27f4d2", mclaren: "#ff8000",
  aston_martin: "#229971", alpine: "#0093cc", williams: "#64c4ff", rb: "#6692ff",
  haas: "#b6babd", sauber: "#52e252", audi: "#f50537", cadillac: "#a6a8aa",
};
function teamColor(id) {
  if (TEAM_COLORS[id]) return TEAM_COLORS[id];
  let h = 0;
  for (const ch of String(id || "x")) h = (h * 31 + ch.charCodeAt(0)) % 360;
  return `hsl(${h} 55% 55%)`;
}
const teamStyle = (id) => `style="--team:${teamColor(id)}"`;

const FLAGS = {Australia:"🇦🇺",China:"🇨🇳",Japan:"🇯🇵",Bahrain:"🇧🇭","Saudi Arabia":"🇸🇦",USA:"🇺🇸","United States":"🇺🇸",Italy:"🇮🇹",Monaco:"🇲🇨",Spain:"🇪🇸",Canada:"🇨🇦",Austria:"🇦🇹",UK:"🇬🇧","United Kingdom":"🇬🇧",Belgium:"🇧🇪",Hungary:"🇭🇺",Netherlands:"🇳🇱",Azerbaijan:"🇦🇿",Singapore:"🇸🇬",Mexico:"🇲🇽",Brazil:"🇧🇷",Qatar:"🇶🇦",UAE:"🇦🇪",Portugal:"🇵🇹",Turkey:"🇹🇷",Germany:"🇩🇪",France:"🇫🇷",Malaysia:"🇲🇾",Russia:"🇷🇺"};
const flag = (country) => FLAGS[country] || "🏁";
function podium(rows) {
  return '<div class="podium">' + [rows[1], rows[0], rows[2]].map((r) => !r ? "" : `<div class="pod p${r.pos}" ${teamStyle(r.team_id)}>
    <span class="pod-code">${esc(r.code)}</span><span class="pod-name">${esc(r.family || r.name)}</span>
    <div class="pod-block"><b>${r.pos}</b></div><span class="pod-time">${esc(r.time)}</span></div>`).join("") + "</div>";
}

/* ======================= сеть ======================= */
async function api(path, opts) {
  const o = opts || {};
  const headers = {};
  if (tg && tg.initData) headers.Authorization = "tma " + tg.initData;
  if (o.body !== undefined) headers["Content-Type"] = "application/json";
  const res = await fetch(path, {
    method: o.method || "GET", headers, body: o.body !== undefined ? JSON.stringify(o.body) : undefined,
  });
  let data = {};
  try { data = await res.json(); } catch (e) { /* пустой ответ */ }
  if (!res.ok) {
    const err = new Error(data.error || "http_" + res.status);
    err.code = data.error || "http_" + res.status;
    throw err;
  }
  return data;
}
async function cached(path, ttl) {
  const hit = S.cache.get(path);
  if (hit && hit.exp > Date.now()) return hit.data;
  const data = await api(path);
  S.cache.set(path, { exp: Date.now() + (ttl || 45000), data });
  return data;
}

/* ======================= утилиты интерфейса ======================= */
function fmtWhen(iso) {
  if (!iso) return "—";
  return new Intl.DateTimeFormat(locale(), {
    weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  }).format(new Date(iso));
}
function fmtDate(iso) {
  if (!iso) return "";
  return new Intl.DateTimeFormat(locale(), { day: "numeric", month: "short" }).format(new Date(iso.length === 10 ? iso + "T12:00:00" : iso));
}
function parts(ms) {
  const total = Math.max(0, Math.floor(ms / 1000));
  return { d: Math.floor(total / 86400), h: Math.floor(total / 3600) % 24, m: Math.floor(total / 60) % 60, s: total % 60 };
}
const pad = (n) => String(n).padStart(2, "0");
function shortLeft(ms) {
  const p = parts(ms);
  return p.d > 0 ? `${p.d}${t("d")} ${p.h}${t("h")}` : `${pad(p.h)}:${pad(p.m)}:${pad(p.s)}`;
}

function toast(msg, kind) {
  const el = $("#toast");
  el.textContent = msg;
  el.className = "toast" + (kind ? " " + kind : "");
  el.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { el.hidden = true; }, 2600);
  if (tg && tg.HapticFeedback && kind) {
    try { tg.HapticFeedback.notificationOccurred(kind === "good" ? "success" : "error"); } catch (e) { /* ок */ }
  }
}

function errorMessage(e) {
  if (e && e.code === "unauthorized") return t("err_unauthorized");
  if (e && e.code === "upstream") return t("err_upstream");
  return t("loading_err");
}

function setView(html, rid) {
  if (rid !== undefined && rid !== S.renderId) return false;
  $("#view").innerHTML = html;
  return true;
}
const skeleton = () => '<div class="skeleton"></div>'.repeat(5);
const errorBox = (e) => `<div class="err"><p>${esc(errorMessage(e))}</p><button class="btn ghost" data-act="retry">${t("retry")}</button></div>`;

function gantry(on, big) {
  const cols = Array.from({ length: 5 }, (_, i) => `<b class="col${i < on ? " on" : ""}"><i></i><i></i></b>`).join("");
  return `<div class="gantry${big ? " big" : ""}" aria-hidden="true">${cols}</div>`;
}
function setGantry(on) {
  document.querySelectorAll(".gantry .col").forEach((el, i) => el.classList.toggle("on", i < on));
}

/* ======================= карточка-«шторка» ======================= */
function openSheet(html) {
  $("#sheet-body").innerHTML = html;
  $("#sheet").hidden = false;
  if (tg && tg.BackButton) { tg.BackButton.show(); }
}
function closeSheet() {
  $("#sheet").hidden = true;
  $("#sheet-body").innerHTML = "";
  S.stake = null;
  if (tg && tg.BackButton) { tg.BackButton.hide(); }
}

/* ======================= навигация ======================= */
const ICONS = {
  race: '<path d="M5 21V4m0 0h11l-2 4 2 4H5"/>',
  cal: '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
  grid: '<path d="M5 20V10M12 20V4M19 20v-7"/>',
  play: '<circle cx="12" cy="12" r="8"/><path d="M9.5 12h5M12 9.5v5"/>',
  me: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-4 4-6 8-6s7 2 8 6"/>',
};
const TABS = ["race", "cal", "grid", "play", "me"];

function renderTabbar() {
  $("#tabbar").innerHTML = '<div class="inner">' + TABS.map((k) => `
    <button class="tab" data-act="tab" data-tab="${k}" ${S.tab === k ? 'aria-current="page"' : ""}>
      <svg viewBox="0 0 24 24">${ICONS[k]}</svg><span>${t("tab_" + k)}</span>
    </button>`).join("") + "</div>";
}

function go(tab) {
  S.tab = tab;
  renderTabbar();
  render();
  window.scrollTo(0, 0);
}

function render() {
  const rid = ++S.renderId;
  if (S.react && !(S.tab === "play" && S.playTab === "start")) { reactClear(); S.react = null; }
  setView(skeleton(), rid);
  const fn = { race: renderRace, cal: renderCalendar, grid: renderGrid, play: renderPlay, me: renderMe }[S.tab];
  fn(rid).catch((e) => setView(errorBox(e), rid));
}

/* ======================= обратный отсчёт ======================= */
function tick() {
  const now = Date.now();
  document.querySelectorAll("[data-cd]").forEach((el) => {
    const left = new Date(el.dataset.cd).getTime() - now;
    if (el.dataset.mode === "big") {
      const p = parts(left);
      const cells = el.querySelectorAll(".n");
      const vals = cells.length === 4 ? [p.d, p.h, p.m, p.s] : [p.h + p.d * 24, p.m, p.s];
      cells.forEach((n, i) => { n.textContent = pad(vals[i]); });
    } else {
      el.textContent = shortLeft(left);
    }
    if (left <= 0 && !el.dataset.fired && now - (S.lastFire || 0) > 15000) {
      el.dataset.fired = "1";
      S.lastFire = now;
      setTimeout(() => { if (S.tab === "race" || S.tab === "play") render(); }, 1200);
    }
  });
}
setInterval(tick, 1000);

function bigCountdown(iso, lessThanDay) {
  const units = lessThanDay ? ["h", "m", "s"] : ["d", "h", "m", "s"];
  return `<div class="cd" data-cd="${esc(iso)}" data-mode="big" role="timer">` +
    units.map((u) => `<span class="u"><b class="n">00</b><small>${t(u)}</small></span>`).join("") + "</div>";
}

/* ======================= вкладка «Гонка» ======================= */
function towerRowResult(r) {
  return `<div class="row"><span class="pos">${r.pos || "–"}</span><span class="bar" ${teamStyle(r.team_id)}></span>
    <span class="code">${esc(r.code)}</span><span class="who"><b>${esc(r.name)}</b><span>${esc(r.team)}</span></span>
    <span class="when">${esc(r.time)}</span></div>`;
}

async function renderRace(rid) {
  const [cal, last] = await Promise.all([cached("/api/calendar", 60000), cached("/api/last", 120000)]);
  const race = cal.races.find((r) => r.round === cal.next_round);
  const now = Date.now();
  let html = "";
  let lightsOn = 5;

  if (race) {
    const start = race.start ? new Date(race.start).getTime() : null;
    const live = start !== null && now >= start;
    if (live) lightsOn = 0;
    const nextIdx = race.sessions.findIndex((s) => new Date(s.at).getTime() > now);
    html += `<section class="hero"><div class="hero-flag" aria-hidden="true">${flag(race.country)}</div>${gantry(S.gantryPlayed ? lightsOn : 0)}
      <h1 class="title">${esc(race.name)}</h1>
      <p class="sub">${t("round", { n: race.round })}, ${esc(race.place)}, ${esc(race.country)}</p>`;
    if (live) {
      html += `<p class="live-note">${t("race_live")}</p><p class="sub">${t("lights_out")}</p>`;
    } else if (start !== null) {
      html += bigCountdown(race.start, start - now < 86400000) + `<p class="sub">${t("until_race")}</p>`;
    } else {
      html += `<p class="live-note">${fmtDate(race.date)}</p>`;
    }
    html += `</section><h2 class="h2">${t("weekend")}</h2><div class="tower">` +
      race.sessions.map((s, i) => {
        const past = new Date(s.at).getTime() <= now;
        return `<div class="row${past ? " dim" : ""}"><span class="dot${i === nextIdx ? "" : " off"}"></span>
          <span class="who"><b>${t("s_" + s.key)}</b></span><span class="when">${fmtWhen(s.at)}</span></div>`;
      }).join("") + "</div>";
  } else {
    html += `<section class="hero">${gantry(0)}<h1 class="title">${t("season_over")}</h1><p class="sub">${t("season_over_sub")}</p></section>`;
  }

  if (last.race) {
    html += `<h2 class="h2">${t("last_race")}: ${esc(last.race.name)}</h2>
      ${podium(last.rows.slice(0, 3))}`;
    if (last.rows.length > 3) {
      html += `<details class="race" style="margin-top:8px"><summary><span class="who"><b>${t("all_results")}</b></span></summary>
        <div>${last.rows.slice(3).map(towerRowResult).join("")}</div></details>`;
    }
  } else {
    html += `<p class="empty">${t("no_results")}</p>`;
  }

  if (!setView(html, rid)) return;
  if (!S.gantryPlayed && race) {
    S.gantryPlayed = true;
    for (let i = 1; i <= lightsOn; i++) setTimeout(() => setGantry(i), 260 * i);
  }
  tick();
}

/* ======================= вкладка «Календарь» ======================= */
async function renderCalendar(rid) {
  const cal = await cached("/api/calendar", 60000);
  if (!cal.races.length) return void setView(`<p class="empty">${t("season_over_sub")}</p>`, rid);
  const html = cal.races.map((r) => {
    const isNext = r.round === cal.next_round;
    return `<details class="race${r.done ? " done" : ""}${isNext ? " next" : ""}" ${isNext ? "open" : ""}>
      <summary><span class="round">${r.round}</span>
        <span class="who"><b><i class="flag-sm">${flag(r.country)}</i>${esc(r.name)}</b><span>${esc(r.place)}, ${esc(r.country)}</span></span>
        <span class="date">${fmtDate(r.date)}</span></summary>
      ${r.sessions.map((s) => `<div class="sess${isNext && s.key === "race" ? " is-next" : ""}"><span>${t("s_" + s.key)}</span><span>${fmtWhen(s.at)}</span></div>`).join("")}
    </details>`;
  }).join("");
  if (!setView(html, rid)) return;
  const open = $("details.next");
  if (open) open.scrollIntoView({ block: "center" });
}

/* ======================= вкладка «Зачёт» ======================= */
async function renderGrid(rid) {
  const kind = S.gridTab;
  const data = await cached("/api/standings/" + kind, 90000);
  const seg = `<div class="seg" role="group">
    <button data-act="grid-tab" data-v="drivers" aria-pressed="${kind === "drivers"}">${t("drivers")}</button>
    <button data-act="grid-tab" data-v="teams" aria-pressed="${kind === "teams"}">${t("teams")}</button></div>`;
  if (!data.rows.length) return void setView(seg + `<p class="empty">${t("no_standings")}</p>`, rid);
  const top = Math.max(1, ...data.rows.map((r) => Number(r.points) || 0));
  const pct = (r) => Math.round(((Number(r.points) || 0) / top) * 100);
  let rows;
  if (kind === "drivers") {
    S.drivers = new Map(data.rows.map((r) => [r.id, r]));
    rows = data.rows.map((r) => `<button class="row team-row p${r.pos}" data-act="driver" data-id="${esc(r.id)}" style="--team:${teamColor(r.team_id)};--pct:${pct(r)}%">
      <span class="pos">${r.pos || "–"}</span><span class="bar" ${teamStyle(r.team_id)}></span>
      <span class="code">${esc(r.code)}</span><span class="who"><b>${esc(r.name)}</b><span>${esc(r.team)}</span></span>
      <span class="pts">${r.points}</span><span class="meter"></span></button>`).join("");
  } else {
    S.teams = new Map(data.rows.map((r) => [r.id, r]));
    rows = data.rows.map((r) => `<button class="row team-row p${r.pos}" data-act="team" data-id="${esc(r.id)}" style="--team:${teamColor(r.id)};--pct:${pct(r)}%">
      <span class="pos">${r.pos || "–"}</span><span class="bar" ${teamStyle(r.id)}></span>
      <span class="who"><b>${esc(r.name)}</b><span>${t("wins")}: ${r.wins}</span></span>
      <span class="pts">${r.points}</span><span class="meter"></span></button>`).join("");
  }
  setView(seg + `<div class="tower">${rows}</div>`, rid);
}

function careerBlock(c) {
  if (!c) return "";
  const hist = (c.history || []).map((h) => `<div class="row"><span class="code" style="width:48px">${esc(h.season)}</span>
    <span class="who"><b>${esc(h.team)}</b></span><span class="when">P${h.pos || "–"}</span><span class="pts">${h.points}</span></div>`).join("");
  return `<div class="stats four">
      <div><b>${c.seasons}</b><span>${t("seasons")}</span></div><div><b>${c.titles}</b><span>${t("titles")}</span></div>
      <div><b>${c.wins}</b><span>${t("wins")}</span></div><div><b>${c.best ? "P" + c.best : "–"}</b><span>${t("best_finish")}</span></div></div>
    ${hist ? `<h3 class="h2" style="margin-top:14px">${t("recent")}</h3><div class="tower">${hist}</div>` : ""}`;
}

async function openDriver(id) {
  const base = S.drivers.get(id);
  if (!base) return;
  const head = `<div class="drv-head" ${teamStyle(base.team_id)}><div class="drv-num">${esc(base.number || base.code)}</div>
    <div><h2 class="title" style="font-size:22px">${esc(base.name)}</h2><p class="sub">${esc(base.team)}${base.nat ? ", " + esc(base.nat) : ""}</p></div></div>
    <div class="stats"><div><b>${base.pos || "–"}</b><span>${t("position")}</span></div>
    <div><b>${base.points}</b><span>${t("points")}</span></div><div><b>${base.wins}</b><span>${t("wins")}</span></div></div>`;
  openSheet(head + '<div id="career"><div class="skeleton"></div></div>');
  try {
    const data = await cached("/api/driver/" + encodeURIComponent(id), 600000);
    const slot = $("#career");
    if (slot) slot.innerHTML = careerBlock(data.career);
  } catch (e) { const slot = $("#career"); if (slot) slot.innerHTML = ""; }
}

async function openTeam(id) {
  const base = S.teams.get(id);
  if (!base) return;
  const head = `<div class="drv-head" ${teamStyle(id)}><div class="drv-num">${base.pos || "–"}</div>
    <div><h2 class="title" style="font-size:22px">${esc(base.name)}</h2><p class="sub">${esc(base.nat)}</p></div></div>
    <div class="stats"><div><b>${base.pos || "–"}</b><span>${t("position")}</span></div>
    <div><b>${base.points}</b><span>${t("points")}</span></div><div><b>${base.wins}</b><span>${t("wins")}</span></div></div>`;
  openSheet(head + '<div id="career"><div class="skeleton"></div></div>');
  try {
    const data = await cached("/api/team/" + encodeURIComponent(id), 600000);
    const slot = $("#career");
    if (!slot) return;
    const drivers = data.drivers.map((d) => `<div class="row"><span class="code">${esc(d.code)}</span>
      <span class="who"><b>${esc(d.name)}</b></span><span class="pts">${d.points}</span></div>`).join("");
    slot.innerHTML = (drivers ? `<div class="tower" style="margin-bottom:12px">${drivers}</div>` : "") + careerBlock(data.career);
  } catch (e) { const slot = $("#career"); if (slot) slot.innerHTML = ""; }
}

/* ======================= вкладка «Игры» ======================= */
const wallet = () => `<div class="wallet"><div><span class="muted small">${t("coins")}</span><div class="num"><span class="coin"></span>${fmt(S.me.coins)}</div></div></div>`;

async function renderPlay(rid) {
  Object.assign(S.me, await api("/api/me"));
  const tabs = ["bets", "duels", "start", "top"];
  const seg = `<div class="seg" role="group">${tabs.map((k) =>
    `<button data-act="play-tab" data-v="${k}" aria-pressed="${S.playTab === k}">${t(k)}</button>`).join("")}</div>`;
  let body = "";
  if (S.playTab === "bets" || S.playTab === "duels") body = await playBetsHtml();
  else if (S.playTab === "start") body = reactionHtml();
  else body = await topHtml();
  if (!setView(wallet() + seg + body + `<p class="fine">${t("virtual_note")}</p>`, rid)) return;
  tick();
}

function betRow(b) {
  const label = b.kind === "h2h" ? `${esc(b.pick_name)} ${t("vs")} ${esc(b.opponent_name)}` : esc(b.pick_name);
  const payout = b.status === "won" ? ` +${fmt(b.payout)}` : "";
  return `<div class="row"><span class="who"><b>${label}</b><span>${t("k_" + b.kind)}, ${fmt(b.stake)} × ${b.odds.toFixed(2)}${b.race && b.status !== "open" ? ", " + esc(b.race) : ""}</span></span>
    <span class="badge ${b.status}">${t("st_" + b.status)}${payout}</span></div>`;
}

async function playBetsHtml() {
  const data = await api("/api/markets");
  S.me.coins = data.coins;
  if (!data.race) return `<p class="empty">${t("no_race_bets")}</p>`;
  const mine = data.my_bets;
  S.markets = data.markets;
  const head = data.open
    ? `<p class="notice">${esc(data.race.name)}. ${t("closes_in", { t: `<span data-cd="${esc(data.closes_at)}">…</span>` })}</p>`
    : `<p class="notice">${esc(data.race.name)}. ${t("closed")}</p>`;
  let body = "";
  if (S.playTab === "bets") {
    const kinds = ["winner", "podium", "pole"];
    const chips = `<div class="chips">${kinds.map((k) =>
      `<button class="chip" data-act="market" data-v="${k}" aria-pressed="${S.market === k}">${t("k_" + k)}</button>`).join("")}</div>`;
    const placed = mine.find((b) => b.kind === S.market);
    const list = data.markets[S.market].slice().sort((a, b) => a.odds - b.odds).map((e) => `
      <button class="row" data-act="pick" data-kind="${S.market}" data-id="${esc(e.id)}" ${data.open && !placed ? "" : "disabled"}>
        <span class="bar" ${teamStyle(e.team_id)}></span><span class="code">${esc(e.code)}</span>
        <span class="who"><b>${esc(e.name)}</b><span>${esc(e.team)}</span></span><span class="odds">${e.odds.toFixed(2)}</span></button>`).join("");
    body = chips + `<p class="sub" style="margin-bottom:8px">${t("k_" + S.market + "_hint")}</p>` +
      (placed ? `<p class="notice">${t("already_bet", { k: t("k_" + S.market) })}</p>` : "") +
      `<div class="tower">${list}</div>`;
  } else {
    const mineH2h = mine.filter((b) => b.kind === "h2h");
    body = `<p class="sub" style="margin-bottom:8px">${t("duel_hint")}</p>` + data.markets.h2h.map((m) => {
      const taken = mineH2h.find((b) => b.pick === m.a.id || b.pick === m.b.id);
      const btn = (e) => `<button data-act="pick" data-kind="h2h" data-id="${esc(e.id)}" data-ref="${esc(m.team_id)}"
        aria-pressed="${taken && taken.pick === e.id}" ${data.open && !taken ? "" : "disabled"} ${teamStyle(m.team_id)}>
        <b>${esc(e.code)}</b><span>${esc(e.name)}</span><span class="odds">${e.odds.toFixed(2)}</span></button>`;
      return `<div class="card"><b>${esc(m.team)}</b><div class="duel">${btn(m.a)}${btn(m.b)}</div></div>`;
    }).join("");
  }
  const mineHtml = mine.length ? `<h2 class="h2">${t("your_bets")}</h2><div class="tower">${mine.map(betRow).join("")}</div>` : "";
  return head + body + mineHtml;
}

/* --- окно ставки --- */
function findSelection(kind, id, ref) {
  if (kind === "h2h") {
    const m = S.markets.h2h.find((x) => x.team_id === ref);
    if (!m) return null;
    const own = id === m.a.id ? m.a : m.b;
    const other = id === m.a.id ? m.b : m.a;
    return { kind, pick: id, ref, odds: own.odds, label: `${own.name} ${t("vs")} ${other.name}` };
  }
  const e = S.markets[kind].find((x) => x.id === id);
  return e ? { kind, pick: id, ref: "", odds: e.odds, label: e.name } : null;
}

function stakeSheet() {
  const s = S.stake;
  const lim = S.me.limits;
  const max = Math.min(lim.max_bet, S.me.coins);
  if (max < lim.min_bet) {
    return `<h2 class="title" style="font-size:22px">${esc(s.label)}</h2><p class="notice" style="margin-top:12px">${t("low_coins")}</p>
      <button class="btn ghost" data-act="close-sheet">${t("close")}</button>`;
  }
  const amounts = [25, 50, 100, 250, 500].filter((a) => a >= lim.min_bet && a <= max);
  return `<p class="sub">${t("k_" + s.kind)}, ${t("odds")} ${s.odds.toFixed(2)}</p>
    <h2 class="title" style="font-size:22px;margin-bottom:6px">${esc(s.label)}</h2>
    <div class="chips">${amounts.map((a) => `<button class="chip" data-act="stake-chip" data-v="${a}" aria-pressed="${s.amount === a}">${a}</button>`).join("")}</div>
    <label class="sub" for="stake-input">${t("stake")} (${lim.min_bet}–${max})</label>
    <input id="stake-input" type="number" inputmode="numeric" min="${lim.min_bet}" max="${max}" value="${s.amount}"
      style="width:100%;min-height:48px;margin:6px 0 10px;padding:0 12px;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--text);font:inherit;font-size:18px">
    <p class="sub" style="margin-bottom:14px">${t("payout")}: <b id="payout-preview" class="num" style="color:var(--text)">${fmt(Math.floor(s.amount * s.odds))}</b></p>
    <button class="btn" data-act="place-bet" id="place-btn">${t("place_bet")}</button>`;
}

function updateStakePreview() {
  const s = S.stake;
  if (!s) return;
  const input = $("#stake-input");
  const v = parseInt(input ? input.value : s.amount, 10) || 0;
  s.amount = v;
  const out = $("#payout-preview");
  if (out) out.textContent = fmt(Math.floor(v * s.odds));
  document.querySelectorAll('[data-act="stake-chip"]').forEach((c) => c.setAttribute("aria-pressed", String(Number(c.dataset.v) === v)));
}

async function placeBet() {
  const s = S.stake;
  if (!s) return;
  const lim = S.me.limits;
  const amount = parseInt(s.amount, 10);
  if (!(amount >= lim.min_bet && amount <= Math.min(lim.max_bet, S.me.coins))) return toast(t("bet_funds"), "bad");
  const btn = $("#place-btn");
  if (btn) btn.disabled = true;
  try {
    const res = await api("/api/bets", { method: "POST", body: { kind: s.kind, pick: s.pick, ref: s.ref, stake: amount } });
    S.me.coins = res.coins;
    closeSheet();
    toast(t("bet_placed"), "good");
    render();
  } catch (e) {
    if (btn) btn.disabled = false;
    const map = { closed: "bet_closed", duplicate: "bet_dup", no_funds: "bet_funds", bad_pick: "bet_bad", bad_stake: "bet_funds" };
    toast(t(map[e.code] || "loading_err"), "bad");
    if (e.code === "closed" || e.code === "duplicate") { closeSheet(); render(); }
  }
}

/* --- игра «Огни погасли» --- */
function reactionHtml() {
  const r = S.react || (S.react = { phase: "idle", msg: "", cls: "", time: "", timers: [] });
  const best = S.me.best_reaction ? t("react_best", { n: S.me.best_reaction }) : "";
  const label = r.phase === "idle" ? t("react_start") : r.phase === "go" ? t("react_tap") : t("react_wait");
  return `<div class="react">${gantry(r.phase === "idle" ? 0 : 5, true)}
    <div class="time num" id="r-time">${esc(r.time)}</div>
    <p class="msg ${r.cls}" id="r-msg">${esc(r.msg || t("react_intro"))}</p>
    <button class="btn${r.phase === "lights" || r.phase === "hold" ? " armed" : r.phase === "go" ? " now" : ""}" id="go-btn" data-act="react">${label}</button>
    <p class="fine" id="r-meta">${[best, t("react_runs", { n: S.me.plays_left })].filter(Boolean).join(". ")}</p></div>`;
}

function reactUi(patch) {
  const r = S.react;
  Object.assign(r, patch);
  const btn = $("#go-btn");
  if (!btn) return;
  btn.className = "btn" + (r.phase === "lights" || r.phase === "hold" ? " armed" : r.phase === "go" ? " now" : "");
  btn.textContent = r.phase === "idle" ? t("react_start") : r.phase === "go" ? t("react_tap") : t("react_wait");
  $("#r-time").textContent = r.time;
  const msg = $("#r-msg");
  msg.textContent = r.msg || t("react_intro");
  msg.className = "msg " + r.cls;
  const best = S.me.best_reaction ? t("react_best", { n: S.me.best_reaction }) : "";
  $("#r-meta").textContent = [best, t("react_runs", { n: S.me.plays_left })].filter(Boolean).join(". ");
}

function reactClear() {
  (S.react.timers || []).forEach(clearTimeout);
  S.react.timers = [];
}

async function reactPress() {
  const r = S.react;
  if (r.phase === "idle") {
    reactUi({ phase: "lights", msg: "", cls: "", time: "" });
    const seq = (r.seq = (r.seq || 0) + 1);
    let info;
    try { info = await api("/api/reaction/start", { method: "POST", body: {} }); }
    catch (e) { reactUi({ phase: "idle" }); return toast(errorMessage(e), "bad"); }
    if (r.phase !== "lights" || r.seq !== seq) return;  // игрок успел нажать до ответа сервера: фальстарт
    S.me.plays_left = info.plays_left;
    r.token = info.token;
    setGantry(0);
    for (let i = 1; i <= 5; i++) r.timers.push(setTimeout(() => setGantry(i), (info.lights_ms / 5) * i));
    r.timers.push(setTimeout(() => reactUi({ phase: "hold" }), info.lights_ms));
    r.timers.push(setTimeout(() => {
      setGantry(0);
      r.t0 = performance.now();
      reactUi({ phase: "go" });
    }, info.lights_ms + info.delay_ms));
  } else if (r.phase === "lights" || r.phase === "hold") {
    reactClear();
    setGantry(0);
    reactUi({ phase: "idle", msg: t("react_false"), cls: "bad", time: "" });
    if (tg && tg.HapticFeedback) { try { tg.HapticFeedback.notificationOccurred("error"); } catch (e) { /* ок */ } }
  } else if (r.phase === "go") {
    const ms = Math.round(performance.now() - r.t0);
    reactUi({ phase: "idle", time: ms + " ms", msg: "", cls: "" });
    try {
      const res = await api("/api/reaction/finish", { method: "POST", body: { token: r.token, reaction_ms: ms } });
      S.me.coins = res.coins;
      S.me.best_reaction = res.best;
      S.me.plays_left = res.plays_left;
      const w = $(".wallet .num");
      if (w) w.innerHTML = `<span class="coin"></span>${fmt(res.coins)}`;
      reactUi({ msg: res.rewarded ? t("react_reward", { n: res.reward }) : t("react_no_reward"), cls: res.rewarded ? "good" : "" });
    } catch (e) {
      reactUi({ msg: e.code === "invalid_time" || e.code === "bad_token" ? t("react_invalid") : errorMessage(e), cls: "bad" });
    }
  }
}

/* --- рейтинги --- */
async function topHtml() {
  const data = await api(`/api/leaderboard?scope=${S.scope}&board=${S.board}`);
  const scopeSeg = `<div class="seg" role="group">${["global", "friends"].map((k) =>
    `<button data-act="scope" data-v="${k}" aria-pressed="${S.scope === k}">${t("scope_" + k)}</button>`).join("")}</div>`;
  const boardSeg = `<div class="seg" role="group">${["coins", "reaction"].map((k) =>
    `<button data-act="board" data-v="${k}" aria-pressed="${S.board === k}">${t("board_" + k)}</button>`).join("")}</div>`;
  const value = (v) => (S.board === "coins" ? fmt(v) : v + " ms");
  const rows = data.rows.length
    ? `<div class="tower">${data.rows.map((r) => `<div class="row${r.me ? " mine" : ""}">
        <span class="pos">${r.rank}</span><span class="who"><b>${esc(r.name)}</b></span><span class="pts">${value(r.value)}</span></div>`).join("")}</div>`
    : `<p class="empty">${t("no_rank")}</p>`;
  const rank = data.me_rank && !data.rows.some((r) => r.me) ? `<p class="sub" style="margin-top:8px">${t("your_rank", { n: data.me_rank })}</p>` : "";
  const invite = S.me.invite_link
    ? `<h2 class="h2">${t("invite")}</h2><p class="sub" style="margin-bottom:10px">${t("invite_sub", { n: 100 })}</p>
       <button class="btn ghost" data-act="invite">${t("invite")}</button>` : "";
  return scopeSeg + boardSeg + rows + rank + invite;
}

/* ======================= вкладка «Профиль» ======================= */
async function renderMe(rid) {
  const [me, hist] = await Promise.all([api("/api/me"), api("/api/bets/history")]);
  S.me = me;
  S.lang = me.lang;
  const seg = ["en", "ru"].map((l) =>
    `<button data-act="lang" data-v="${l}" aria-pressed="${me.lang === l}">${l === "en" ? "English" : "Русский"}</button>`).join("");
  const html = `<div class="me-head"><div class="avatar">${esc((me.name || "?").slice(0, 1).toUpperCase())}</div>
      <div><h1 class="title" style="font-size:22px">${esc(me.name)}</h1><p class="sub">${t("friends", { n: me.friends })}</p></div></div>
    ${wallet()}
    <div class="card"><div class="line"><div><b>${t("daily")}</b><p class="sub">${t("streak", { n: me.streak })}</p></div></div>
      <button class="btn green" data-act="daily" ${me.daily_available ? "" : "disabled"}>${me.daily_available ? t("daily_claim") : t("daily_done")}</button></div>
    <div class="card">
      <div class="line"><b>${t("language")}</b></div><div class="seg" role="group" style="margin:0">${seg}</div>
      <div class="line"><div><b>${t("notifications")}</b><p class="sub">${t("notifications_sub")}</p></div>
        <label class="switch"><input type="checkbox" data-act="notify" ${me.notify ? "checked" : ""} aria-label="${t("notifications")}"><span></span></label></div>
    </div>
    ${me.invite_link ? `<button class="btn ghost" data-act="invite">${t("invite")}</button>` : ""}
    <h2 class="h2">${t("history")}</h2>
    ${hist.bets.length ? `<div class="tower">${hist.bets.map(betRow).join("")}</div>` : `<p class="empty">${t("no_bets")}</p>`}
    <p class="fine">${t("virtual_note")}</p>`;
  setView(html, rid);
}

/* ======================= события ======================= */
document.addEventListener("click", async (ev) => {
  const el = ev.target.closest("[data-act]");
  if (!el || el.disabled) return;
  const act = el.dataset.act;
  const v = el.dataset.v;
  try {
    switch (act) {
      case "tab": return go(el.dataset.tab);
      case "retry": return S.me ? render() : boot();
      case "close-sheet": return closeSheet();
      case "grid-tab": S.gridTab = v; return render();
      case "play-tab": if (S.react) reactClear(); S.react = null; S.playTab = v; return render();
      case "market": S.market = v; return render();
      case "scope": S.scope = v; return render();
      case "board": S.board = v; return render();
      case "driver": return openDriver(el.dataset.id);
      case "team": return openTeam(el.dataset.id);
      case "pick": {
        const sel = findSelection(el.dataset.kind, el.dataset.id, el.dataset.ref || "");
        if (!sel) return;
        S.stake = Object.assign(sel, { amount: Math.min(100, S.me.limits.max_bet, Math.max(S.me.coins, 0)) });
        if (S.stake.amount < S.me.limits.min_bet) S.stake.amount = S.me.limits.min_bet;
        return openSheet(stakeSheet());
      }
      case "stake-chip": { const i = $("#stake-input"); if (i) i.value = v; return updateStakePreview(); }
      case "place-bet": return placeBet();
      case "react": return reactPress();
      case "invite": {
        const url = "https://t.me/share/url?url=" + encodeURIComponent(S.me.invite_link) + "&text=" + encodeURIComponent(t("invite_text"));
        if (tg && tg.openTelegramLink) tg.openTelegramLink(url); else window.open(url, "_blank");
        return;
      }
      case "daily": {
        const res = await api("/api/daily", { method: "POST", body: {} });
        toast(t("daily_got", { n: res.bonus, s: res.streak }), "good");
        return render();
      }
      case "lang": {
        await api("/api/settings", { method: "POST", body: { lang: v } });
        S.lang = v; S.me.lang = v;
        document.documentElement.lang = v;
        renderTabbar();
        return render();
      }
    }
  } catch (e) {
    toast(errorMessage(e), "bad");
  }
});

document.addEventListener("input", (ev) => {
  if (ev.target.id === "stake-input") updateStakePreview();
});
document.addEventListener("change", async (ev) => {
  if (ev.target.dataset && ev.target.dataset.act === "notify") {
    try {
      await api("/api/settings", { method: "POST", body: { notify: ev.target.checked } });
      S.me.notify = ev.target.checked;
      toast(t("saved"), "good");
    } catch (e) { ev.target.checked = !ev.target.checked; toast(errorMessage(e), "bad"); }
  }
});
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !$("#sheet").hidden) closeSheet(); });
if (tg && tg.BackButton) tg.BackButton.onClick(closeSheet);

/* ======================= тема и запуск ======================= */
function applyTheme() {
  const scheme = (tg && tg.colorScheme) || (window.matchMedia && matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  document.documentElement.dataset.theme = scheme;
  const bg = getComputedStyle(document.documentElement).getPropertyValue("--bg").trim();
  try {
    if (tg && tg.setHeaderColor) tg.setHeaderColor(bg);
    if (tg && tg.setBackgroundColor) tg.setBackgroundColor(bg);
    if (tg && tg.setBottomBarColor) tg.setBottomBarColor(getComputedStyle(document.documentElement).getPropertyValue("--surface").trim());
  } catch (e) { /* старые клиенты */ }
}
if (tg && tg.onEvent) tg.onEvent("themeChanged", applyTheme);

async function boot() {
  applyTheme();
  renderTabbar();
  setView(skeleton());
  try {
    S.me = await api("/api/me");
    S.lang = S.me.lang;
    document.documentElement.lang = S.lang;
    const tz = userTz();
    if (tz && tz !== S.me.tz) api("/api/settings", { method: "POST", body: { tz } }).catch(() => {});
    renderTabbar();
    render();
  } catch (e) {
    setView(errorBox(e));
  }
}
boot();
