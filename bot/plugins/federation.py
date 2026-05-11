from __future__ import annotations

import uuid

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from database import async_session_factory
from services.federation_service import FederationService
from services.group_service import GroupService
from services.user_service import UserService
from utils.decorators import admin_only, group_only, owner_only


@group_only
@owner_only
async def newfed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    user = update.effective_user
    if msg is None or user is None:
        return
    name = " ".join(context.args or []).strip()
    if not name:
        await msg.reply_text("🌸 Give this federation a name.")
        return
    async with async_session_factory() as session:
        async with session.begin():
            await UserService.ensure_user(session, user)
            federation = await FederationService.create_federation(
                session, name, user.id
            )
    await msg.reply_text(f"🌸 Federation created: {federation.fed_id}")


@group_only
@admin_only
async def joinfed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    chat = update.effective_chat
    if msg is None or chat is None or not context.args:
        return
    fed_id = uuid.UUID(context.args[0])
    async with async_session_factory() as session:
        async with session.begin():
            await GroupService.ensure_group(session, chat)
            await FederationService.join_group(session, fed_id, chat.id)
    await msg.reply_text("🌸 This group has joined the federation archive.")


def register(app) -> None:
    app.add_handler(CommandHandler("newfed", newfed))
    app.add_handler(CommandHandler("joinfed", joinfed))
