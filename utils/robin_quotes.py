from __future__ import annotations

import random

QUOTES: tuple[str, ...] = (
    '🌸 "The sea of knowledge has no limits." — Nico Robin',
    '🌸 "Archived. Even the Void Century deserves documentation." — Nico Robin',
    '🌸 "Too many words obscure the truth. Slow down." — Nico Robin',
    '🌸 "Authority is a privilege. Use it wisely." — Nico Robin',
    '🌸 "Every great crew began with a single member." — Nico Robin',
)

ACTION_QUOTES: dict[str, tuple[str, ...]] = {
    "ban": ("The sea of knowledge has limits for those who abuse it.",),
    "mute": ("Silence can speak louder than any words.",),
    "warn": ("Consider this a page in your personal Poneglyph.",),
    "kick": ("Some doors close so others may open.",),
    "flood": ("Too many words obscure the truth. Slow down.",),
    "raid": ("An attack from all sides. Activating Hana Hana no Mi...",),
    "captcha_fail": ("The sea does not wait for those who hesitate.",),
    "note": ("Archived. Even the Void Century deserves documentation.",),
    "welcome": ("Every great crew began with a single member.",),
    "promote": ("Authority is a privilege. Use it wisely.",),
}


def random_quote() -> str:
    return random.choice(QUOTES)


def action_quote(action: str) -> str:
    quotes = ACTION_QUOTES.get(action, QUOTES)
    return random.choice(quotes)
