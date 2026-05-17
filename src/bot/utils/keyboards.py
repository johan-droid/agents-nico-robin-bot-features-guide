from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def captcha_keyboard(correct_token: str, decoys: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=token, callback_data=f"captcha:{token}")
        for token in decoys
    ]
    buttons.append(
        InlineKeyboardButton(
            text=correct_token, callback_data=f"captcha:{correct_token}"
        )
    )
    return InlineKeyboardMarkup([buttons])
