from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.federation import Federation, FederationBan, FederationGroup


class FederationService:
    @staticmethod
    async def create_federation(
        session: AsyncSession,
        name: str,
        owner_id: int,
    ) -> Federation:
        federation = Federation(name=name, owner_id=owner_id)
        session.add(federation)
        await session.flush()
        return federation

    @staticmethod
    async def join_group(
        session: AsyncSession,
        fed_id: uuid.UUID,
        group_id: int,
    ) -> FederationGroup:
        result = await session.execute(
            select(FederationGroup).where(
                FederationGroup.fed_id == fed_id,
                FederationGroup.group_id == group_id,
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            link = FederationGroup(
                fed_id=fed_id,
                group_id=group_id,
                joined_at=datetime.now(UTC),
            )
            session.add(link)
        await session.flush()
        return link

    @staticmethod
    async def add_federation_ban(
        session: AsyncSession,
        fed_id: uuid.UUID,
        user_id: int,
        admin_id: int | None,
        reason: str,
    ) -> FederationBan:
        result = await session.execute(
            select(FederationBan).where(
                FederationBan.fed_id == fed_id,
                FederationBan.user_id == user_id,
            )
        )
        ban = result.scalar_one_or_none()
        if ban is None:
            ban = FederationBan(
                fed_id=fed_id,
                user_id=user_id,
                admin_id=admin_id,
                reason=reason,
                created_at=datetime.now(UTC),
            )
            session.add(ban)
        else:
            ban.reason = reason
            ban.admin_id = admin_id
            ban.created_at = datetime.now(UTC)
        await session.flush()
        return ban
