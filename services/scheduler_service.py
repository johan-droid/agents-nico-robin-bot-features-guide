from __future__ import annotations

from datetime import datetime

from tasks.ban_tasks import unban_user_task, unmute_user_task


class SchedulerService:
    @staticmethod
    def schedule_unban(chat_id: int, user_id: int, run_at: datetime) -> str:
        task = unban_user_task.apply_async(args=[chat_id, user_id], eta=run_at)
        return str(task.id)

    @staticmethod
    def schedule_unmute(chat_id: int, user_id: int, run_at: datetime) -> str:
        task = unmute_user_task.apply_async(args=[chat_id, user_id], eta=run_at)
        return str(task.id)
