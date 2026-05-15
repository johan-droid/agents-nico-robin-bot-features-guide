from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.models.warn import Warn
from src.bot.services.user_service import UserService


class WarnService:
    @staticmethod
    async def issue_warn(
        session: AsyncSession,
        group_id: int,
        user_id: int,
        admin_id: int | None,
        reason: str,
    ) -> tuple[Warn, int]:
        warn = Warn(
            group_id=group_id,
            user_id=user_id,
            admin_id=admin_id,
            reason=reason,
            issued_at=datetime.now(UTC),
        )
        session.add(warn)
        await UserService.increment_warn_count(session, user_id)
        await session.flush()
        count = await WarnService.active_warn_count(session, group_id, user_id)
        return warn, count

    @staticmethod
    async def active_warn_count(
        session: AsyncSession,
        group_id: int,
        user_id: int,
    ) -> int:
        result = await session.execute(
            select(func.count(Warn.warn_id)).where(
                Warn.group_id == group_id,
                Warn.user_id == user_id,
                Warn.is_active.is_(True),
            )
        )
        return int(result.scalar_one())

    @staticmethod
    async def list_active_warns(
        session: AsyncSession,
        group_id: int,
        user_id: int,
    ) -> list[Warn]:
        result = await session.execute(
            select(Warn)
            .where(
                Warn.group_id == group_id,
                Warn.user_id == user_id,
                Warn.is_active.is_(True),
            )
            .order_by(Warn.issued_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def reset_warns(session: AsyncSession, group_id: int, user_id: int) -> int:
        result = await session.execute(
            update(Warn)
            .where(
                Warn.group_id == group_id,
                Warn.user_id == user_id,
                Warn.is_active.is_(True),
            )
            .values(is_active=False)
        )
        return int(result.rowcount or 0)

    @staticmethod
    async def mark_latest_auto_action(
        session: AsyncSession,
        warn_id: int,
        action: str,
    ) -> None:
        await session.execute(
            update(Warn).where(Warn.warn_id == warn_id).values(auto_action=action)
        )
