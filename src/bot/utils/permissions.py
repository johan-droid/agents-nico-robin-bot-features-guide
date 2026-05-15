from __future__ import annotations

from telegram import Chat, ChatMember, User
from telegram.ext import ContextTypes

from src.bot.config import settings

ADMIN_STATUSES = {ChatMember.ADMINISTRATOR, ChatMember.OWNER}


def is_sudo(user_id: int | None) -> bool:
    return user_id is not None and user_id in settings.sudo_users


def is_group_chat(chat: Chat | None) -> bool:
    return chat is not None and chat.type in {"group", "supergroup"}


async def is_telegram_admin(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> bool:
    if is_sudo(user_id):
        return True
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ADMIN_STATUSES


async def is_telegram_owner(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> bool:
    if is_sudo(user_id):
        return True
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status == ChatMember.OWNER


def user_display(user: User | None) -> str:
    if user is None:
        return "Unknown"
    if user.username:
        return f"@{user.username}"
    return user.full_name or str(user.id)
