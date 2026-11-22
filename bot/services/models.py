"""Приведение ответов Jolpica к компактным словарям для бота и API."""


def num(value):
    """'25' -> 25, '12.5' -> 12.5, мусор -> 0."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0
    return int(f) if f == int(f) else f


def _pos(value):
    s = str(value or "")
    return int(s) if s.isdigit() else None


def driver_info(d):
    return {
        "id": d["driverId"],
        "code": d.get("code") or d["familyName"][:3].upper(),
        "number": d.get("permanentNumber"),
        "name": f'{d["givenName"]} {d["familyName"]}',
        "family": d["familyName"],
        "nat": d.get("nationality", ""),
    }


def norm_standing(row):
    team = (row.get("Constructors") or [{}])[-1]
    out = driver_info(row["Driver"])
    out.update({
        "pos": _pos(row.get("position")),
        "team": team.get("name", ""),
        "team_id": team.get("constructorId", ""),
        "points": num(row.get("points")),
        "wins": int(num(row.get("wins"))),
    })
    return out


def norm_constructor(row):
    c = row["Constructor"]
    return {
        "pos": _pos(row.get("position")),
        "id": c["constructorId"],
        "name": c["name"],
        "nat": c.get("nationality", ""),
        "points": num(row.get("points")),
        "wins": int(num(row.get("wins"))),
    }


def norm_result(row):
    out = driver_info(row["Driver"])
    out.update({
        "pos": _pos(row.get("position")),
        "grid": _pos(row.get("grid")),
        "team": row["Constructor"]["name"],
        "team_id": row["Constructor"]["constructorId"],
        "points": num(row.get("points")),
        "time": (row.get("Time") or {}).get("time") or row.get("status", ""),
        "status": row.get("status", ""),
    })
    return out
