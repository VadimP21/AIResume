"""Содержит компоненты модуля test_versioning_service."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.models.resume_section import SectionType
from app.services.versioning import VersioningService


@pytest.mark.asyncio
async def test_create_snapshot_serializes_all_section_types() -> None:
    """Проверяет сценарий create snapshot serializes all section types."""
    resume_id = uuid4()
    sections = [
        SimpleNamespace(
            id=uuid4(),
            section_type=section_type,
            position=index,
            content={"value": section_type.value},
        )
        for index, section_type in enumerate(SectionType, start=1)
    ]
    version = SimpleNamespace()
    repository = SimpleNamespace(
        create_version=AsyncMock(return_value=version),
        session=SimpleNamespace(
            commit=AsyncMock(), refresh=AsyncMock(), rollback=AsyncMock()
        ),
    )
    resume = SimpleNamespace(id=resume_id, title="Resume", sections=sections)

    result = await VersioningService(repository).create_snapshot(resume)

    assert result is version
    snapshot = repository.create_version.await_args.kwargs["snapshot"]
    assert [section["type"] for section in snapshot["sections"]] == [
        section_type.value for section_type in SectionType
    ]
    repository.session.commit.assert_awaited_once_with()
