from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from utils.robin_quotes import random_quote


async def robin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message:
        await update.effective_message.reply_text(random_quote())
