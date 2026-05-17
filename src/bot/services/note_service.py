from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.models.note import Note


class NoteService:
    @staticmethod
    async def save_note(
        session: AsyncSession,
        group_id: int,
        name: str,
        content: str,
        created_by: int | None,
        media_id: str | None = None,
    ) -> Note:
        normalized = name.lower()
        result = await session.execute(
            select(Note).where(Note.group_id == group_id, Note.name == normalized)
        )
        note = result.scalar_one_or_none()
        if note is None:
            note = Note(
                group_id=group_id,
                name=normalized,
                content=content,
                media_id=media_id,
                created_by=created_by,
            )
            session.add(note)
        else:
            note.content = content
            note.media_id = media_id
            note.created_by = created_by
        await session.flush()
        return note

    @staticmethod
    async def get_note(session: AsyncSession, group_id: int, name: str) -> Note | None:
        result = await session.execute(
            select(Note).where(Note.group_id == group_id, Note.name == name.lower())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_notes(session: AsyncSession, group_id: int) -> list[Note]:
        result = await session.execute(
            select(Note).where(Note.group_id == group_id).order_by(Note.name.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def delete_note(session: AsyncSession, group_id: int, name: str) -> int:
        result = await session.execute(
            delete(Note).where(Note.group_id == group_id, Note.name == name.lower())
        )
        return int(result.rowcount or 0)
