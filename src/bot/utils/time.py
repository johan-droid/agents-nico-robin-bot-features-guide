from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

_DURATION_RE = re.compile(r"(?P<value>\d+)(?P<unit>[smhd])", re.IGNORECASE)


def parse_duration(value: str | None) -> timedelta | None:
    if not value:
        return None
    total = timedelta()
    for match in _DURATION_RE.finditer(value):
        amount = int(match.group("value"))
        unit = match.group("unit").lower()
        if unit == "s":
            total += timedelta(seconds=amount)
        elif unit == "m":
            total += timedelta(minutes=amount)
        elif unit == "h":
            total += timedelta(hours=amount)
        elif unit == "d":
            total += timedelta(days=amount)
    return total or None


def human_duration(delta: timedelta | None) -> str:
    if delta is None:
        return "forever"
    seconds = int(delta.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def until_datetime(delta: timedelta | None) -> datetime | None:
    if delta is None:
        return None
    return datetime.now(UTC) + delta
