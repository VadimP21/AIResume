"""Проверяет преобразование ORM-сущностей во внутренние DTO."""

from datetime import UTC, datetime
from typing import get_args
from uuid import uuid4

from app.dto import SectionType
from app.models.resume import Resume
from app.models.resume_section import ResumeSection
from app.models.resume_version import ResumeVersion
from app.models.user import User
from app.repositories.mappers import (
    resume_to_dto,
    section_to_dto,
    user_to_auth_dto,
    user_to_dto,
    version_to_dto,
)
from app.repositories.resume import ResumeRepository


def test_user_mappers_separate_authentication_data() -> None:
    """Не передаёт хеш пароля в безопасный DTO пользователя."""
    user = User(
        id=uuid4(),
        email="user@example.com",
        hashed_password="password-hash",
        is_active=True,
        token_version=3,
    )

    user_dto = user_to_dto(user)
    auth_dto = user_to_auth_dto(user)

    assert user_dto.id == user.id
    assert user_dto.email == user.email
    assert not hasattr(user_dto, "password_hash")
    assert auth_dto.password_hash == user.hashed_password
    assert auth_dto.token_version == user.token_version


def test_resume_mappers_convert_loaded_sections() -> None:
    """Преобразует резюме и заранее загруженные секции без запросов."""
    now = datetime.now(UTC)
    resume_id = uuid4()
    first_section = ResumeSection(
        id=uuid4(),
        resume_id=resume_id,
        section_type=SectionType.SUMMARY,
        position=1,
        content={"text": "Summary"},
        created_at=now,
        updated_at=now,
    )
    second_section = ResumeSection(
        id=uuid4(),
        resume_id=resume_id,
        section_type=SectionType.SKILLS,
        position=2,
        content={"skills": []},
        created_at=now,
        updated_at=now,
    )
    resume = Resume(
        id=resume_id,
        user_id=uuid4(),
        title="Resume",
        created_at=now,
        updated_at=now,
        sections=[first_section, second_section],
    )

    section_dto = section_to_dto(first_section)
    resume_dto = resume_to_dto(resume)

    assert section_dto.content == {"text": "Summary"}
    assert resume_dto.id == resume.id
    assert resume_dto.sections == (section_dto, section_to_dto(second_section))


def test_version_mapper_preserves_snapshot() -> None:
    """Преобразует все поля версии резюме."""
    now = datetime.now(UTC)
    version = ResumeVersion(
        id=uuid4(),
        resume_id=uuid4(),
        snapshot={"resume": {"title": "Resume"}},
        created_at=now,
    )

    dto = version_to_dto(version)

    assert dto.id == version.id
    assert dto.resume_id == version.resume_id
    assert dto.snapshot == version.snapshot
    assert dto.created_at == now


def test_public_resume_read_returns_dto() -> None:
    """Фиксирует DTO-контракт публичного read-метода repository."""
    assert {
        item.__name__
        for item in get_args(
            ResumeRepository.get_resume_with_sections.__annotations__["return"]
        )
    } == {"ResumeDTO", "NoneType"}


def test_public_resume_create_returns_dto() -> None:
    """Фиксирует DTO-контракт публичного create-метода repository."""
    assert (
        ResumeRepository.create_resume.__annotations__["return"].__name__ == "ResumeDTO"
    )


def test_public_resume_delete_accepts_identifiers() -> None:
    """Удаление не принимает ORM-объект на публичной границе repository."""
    annotations = ResumeRepository.delete_resume.__annotations__
    assert annotations["resume_id"].__name__ == "UUID"
    assert annotations["user_id"].__name__ == "UUID"
    assert annotations["return"] is bool
