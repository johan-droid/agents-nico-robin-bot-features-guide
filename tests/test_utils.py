from __future__ import annotations

from datetime import timedelta

from src.bot.utils.i18n import gettext
from src.bot.utils.time import parse_duration


def test_i18n_falls_back_to_english() -> None:
    message = gettext("warn.none", locale="missing")

    assert "No active warnings" in message


def test_parse_duration_compounds_units() -> None:
    assert parse_duration("1h30m") == timedelta(hours=1, minutes=30)
