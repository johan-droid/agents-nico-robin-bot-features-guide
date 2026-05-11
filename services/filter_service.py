from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.filter import Filter


@dataclass(frozen=True)
class MatchedFilter:
    filter: Filter
    match_text: str


class FilterService:
    @staticmethod
    async def add_filter(
        session: AsyncSession,
        group_id: int,
        trigger: str,
        response: str | None,
        action: str,
        regex: bool,
        created_by: int | None,
    ) -> Filter:
        normalized = trigger.lower()
        result = await session.execute(
            select(Filter).where(
                Filter.group_id == group_id,
                Filter.trigger == normalized,
            )
        )
        item = result.scalar_one_or_none()
        if item is None:
            item = Filter(
                group_id=group_id,
                trigger=normalized,
                response=response,
                action=action,
                regex=regex,
                created_by=created_by,
            )
            session.add(item)
        else:
            item.response = response
            item.action = action
            item.regex = regex
            item.created_by = created_by
        await session.flush()
        return item

    @staticmethod
    async def remove_filter(session: AsyncSession, group_id: int, trigger: str) -> int:
        result = await session.execute(
            delete(Filter).where(
                Filter.group_id == group_id,
                Filter.trigger == trigger.lower(),
            )
        )
        return int(result.rowcount or 0)

    @staticmethod
    async def list_filters(session: AsyncSession, group_id: int) -> list[Filter]:
        result = await session.execute(
            select(Filter).where(Filter.group_id == group_id).order_by(Filter.trigger)
        )
        return list(result.scalars().all())

    @staticmethod
    async def match_filters(
        session: AsyncSession,
        group_id: int,
        text: str,
    ) -> list[MatchedFilter]:
        items = await FilterService.list_filters(session, group_id)
        lowered = text.lower()
        matches: list[MatchedFilter] = []
        for item in items:
            if item.regex:
                try:
                    match = re.search(item.trigger, text, flags=re.IGNORECASE)
                except re.error:
                    continue
                if match:
                    matches.append(MatchedFilter(item, match.group(0)))
            elif item.trigger in lowered:
                matches.append(MatchedFilter(item, item.trigger))
        return matches
