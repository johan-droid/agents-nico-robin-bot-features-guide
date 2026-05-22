from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient

from src.bot.config import settings
from src.bot.gateway.webhook import create_app


class _DummyPTBApp:
    def __init__(self) -> None:
        self.bot = object()
        self.processed_updates = 0

    async def process_update(self, update) -> None:
        self.processed_updates += 1


def _fake_update_de_json(payload, bot):
    return payload


def _test_client() -> tuple[TestClient, _DummyPTBApp]:
    dummy = _DummyPTBApp()
    app = create_app(dummy)
    return TestClient(app), dummy


@contextmanager
def _set_webhook_security(
    *,
    secret: str,
    require_header: bool,
    path_token: str,
) -> Iterator[None]:
    old_secret = settings.webhook_secret
    old_require_header = settings.webhook_require_secret_header
    old_path_token = settings.webhook_path_token
    settings.webhook_secret = secret
    settings.webhook_require_secret_header = require_header
    settings.webhook_path_token = path_token
    try:
        yield
    finally:
        settings.webhook_secret = old_secret
        settings.webhook_require_secret_header = old_require_header
        settings.webhook_path_token = old_path_token


def test_webhook_accepts_valid_secret_header(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.bot.gateway.webhook.Update.de_json",
        _fake_update_de_json,
    )
    with _set_webhook_security(secret="secret", require_header=True, path_token=""):
        client, dummy = _test_client()
        response = client.post(
            "/telegram/webhook",
            headers={"X-Telegram-Bot-Api-Secret-Token": "secret"},
            json={"update_id": 1},
        )

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert dummy.processed_updates == 1


def test_webhook_rejects_when_secret_header_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.bot.gateway.webhook.Update.de_json",
        _fake_update_de_json,
    )
    with _set_webhook_security(secret="secret", require_header=True, path_token=""):
        client, _ = _test_client()
        response = client.post("/webhook", json={"update_id": 1})

    assert response.status_code == 403


def test_webhook_path_token_is_enforced(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.bot.gateway.webhook.Update.de_json",
        _fake_update_de_json,
    )
    with _set_webhook_security(secret="", require_header=False, path_token="abc123"):
        client, dummy = _test_client()
        ok_response = client.post("/telegram/webhook/abc123", json={"update_id": 7})
        bad_response = client.post("/telegram/webhook/wrong", json={"update_id": 7})

    assert ok_response.status_code == 200
    assert bad_response.status_code == 403
    assert dummy.processed_updates == 1


def test_webhook_rejects_invalid_update_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.bot.gateway.webhook.Update.de_json",
        _fake_update_de_json,
    )
    with _set_webhook_security(secret="", require_header=False, path_token=""):
        client, _ = _test_client()
        response = client.post("/telegram/webhook", json={"message": "missing id"})

    assert response.status_code == 400
