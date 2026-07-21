"""Проверяет контракт внутренних DTO."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.dto import (
    UNSET,
    CreateResumeCommand,
    CreateSectionCommand,
    CreateUserCommand,
    ResumeDTO,
    ResumeSectionDTO,
    ResumeVersionDTO,
    SectionType,
    UpdateResumeCommand,
    UpdateSectionCommand,
    UserAuthDTO,
    UserDTO,
)
from app.models.resume_section import SectionType as ModelSectionType
from app.schemas.section import SectionType as SchemaSectionType


def test_update_commands_distinguish_unset_none_and_value() -> None:
    """Сохраняет три состояния полей частичного обновления."""
    assert UpdateResumeCommand().title is UNSET
    assert UpdateResumeCommand(title=None).title is None
    assert UpdateResumeCommand(title="Python Developer").title == "Python Developer"

    assert UpdateSectionCommand().content is UNSET
    assert UpdateSectionCommand(content=None).content is None
    assert UpdateSectionCommand(content={"text": "Updated"}).content == {
        "text": "Updated"
    }


def test_dtos_are_immutable_and_expose_required_data() -> None:
    """Создаёт DTO и запрещает изменение их полей."""
    now = datetime.now(UTC)
    user_id = uuid4()
    resume_id = uuid4()
    section = ResumeSectionDTO(
        id=uuid4(),
        resume_id=resume_id,
        section_type=SectionType.SUMMARY,
        position=1,
        content={"text": "Summary"},
        created_at=now,
        updated_at=now,
    )
    resume = ResumeDTO(
        id=resume_id,
        user_id=user_id,
        title="Resume",
        created_at=now,
        updated_at=now,
        sections=(section,),
    )
    auth_user = UserAuthDTO(
        id=user_id,
        email="user@example.com",
        password_hash="hash",
        is_active=True,
        token_version=1,
    )

    assert CreateUserCommand(email="user@example.com", password="Password1!").email
    assert CreateResumeCommand(title="Resume").title == "Resume"
    assert (
        CreateSectionCommand(
            section_type=SectionType.SUMMARY,
            content={"text": "Summary"},
        ).section_type
        is SectionType.SUMMARY
    )
    assert (
        UserDTO(
            id=user_id,
            email="user@example.com",
            is_active=True,
            token_version=1,
        ).email
        == "user@example.com"
    )
    assert auth_user.password_hash == "hash"
    assert ResumeVersionDTO(
        id=uuid4(),
        resume_id=resume_id,
        snapshot={"resume": {}},
        created_at=now,
    ).snapshot == {"resume": {}}
    assert resume.sections == (section,)

    with pytest.raises(FrozenInstanceError):
        resume.title = "Updated"  # type: ignore[misc]


def test_dto_modules_do_not_depend_on_infrastructure() -> None:
    """Не допускает инфраструктурные зависимости в DTO-модулях."""
    dto_dir = Path(__file__).parents[3] / "app" / "dto"
    forbidden_imports = ("sqlalchemy", "fastapi", "pydantic", "app.models")

    for dto_module in dto_dir.glob("*.py"):
        source = dto_module.read_text(encoding="utf-8")
        assert not any(import_name in source for import_name in forbidden_imports)


def test_section_type_is_shared_by_model_and_schema() -> None:
    """Использует единый enum секций во всех слоях."""
    assert ModelSectionType is SectionType
    assert SchemaSectionType is SectionType
