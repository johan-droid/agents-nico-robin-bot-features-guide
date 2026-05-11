from __future__ import annotations

import asyncio

import structlog
from telegram import Bot

from config import settings
from tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


async def _send_announcement(chat_id: int, text: str) -> None:
    bot = Bot(settings.bot_token)
    async with bot:
        await bot.send_message(
            chat_id=chat_id, text=text, disable_web_page_preview=True
        )


@celery_app.task(name="tasks.announce_tasks.send_announcement")
def send_announcement_task(chat_id: int, text: str) -> dict[str, int | str]:
    asyncio.run(_send_announcement(chat_id, text))
    logger.info("scheduled_announcement_sent", chat_id=chat_id)
    return {"status": "ok", "chat_id": chat_id}


def schedule_announcement(chat_id: int, text: str, eta) -> str:
    task = send_announcement_task.apply_async(args=[chat_id, text], eta=eta)
    return str(task.id)
