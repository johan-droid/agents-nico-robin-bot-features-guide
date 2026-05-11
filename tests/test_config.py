from __future__ import annotations

from config import Settings


def test_settings_parse_sudo_users() -> None:
    settings = Settings(BOT_TOKEN="token", SUDO_USERS="1, 2,3")

    assert settings.sudo_users == (1, 2, 3)


def test_database_url_is_normalized_for_asyncpg() -> None:
    settings = Settings(
        BOT_TOKEN="token",
        DATABASE_URL="postgres://user:pass@localhost:5432/robin",
    )

    assert settings.database_url.startswith("postgresql+asyncpg://")
