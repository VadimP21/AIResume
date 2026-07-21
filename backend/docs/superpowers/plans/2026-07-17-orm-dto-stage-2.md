# ORM DTO Stage 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить явные функции преобразования ORM-сущностей в DTO.

**Architecture:** Функции располагаются в `app/repositories/mappers`, разделены по областям и явно перечисляют поля. Они не выполняют запросов; `resume_to_dto` использует только уже загруженную коллекцию `resume.sections`.

**Tech Stack:** Python 3.14, SQLAlchemy 2.x models, dataclasses DTO, pytest, Ruff, mypy.

## Global Constraints

- Не менять схему PostgreSQL, HTTP-контракты, сигнатуры repository и транзакционные границы.
- Не использовать reflection или неявную сериализацию.
- Не вызывать маппер резюме до eager loading `Resume.sections`.
- Git-коммит не создаётся без отдельного запроса.

---

### Task 1: Контракт мапперов

**Files:**
- Create: `tests/unit/repositories/test_mappers.py`
- Create: `app/repositories/mappers/__init__.py`
- Create: `app/repositories/mappers/users.py`
- Create: `app/repositories/mappers/resumes.py`
- Create: `app/repositories/mappers/versions.py`

**Interfaces:**
- Produces: `user_to_dto(user: User) -> UserDTO`, `user_to_auth_dto(user: User) -> UserAuthDTO`, `section_to_dto(section: ResumeSection) -> ResumeSectionDTO`, `resume_to_dto(resume: Resume) -> ResumeDTO`, `version_to_dto(version: ResumeVersion) -> ResumeVersionDTO`.

- [x] **Step 1: Write failing tests**

```python
def test_user_mappers_keep_password_hash_only_in_auth_dto() -> None:
    user = User(id=uuid4(), email="user@example.com", hashed_password="hash", is_active=True, token_version=1)
    assert user_to_dto(user).email == user.email
    assert user_to_auth_dto(user).password_hash == "hash"
    assert not hasattr(user_to_dto(user), "password_hash")
```

Add equivalent assertions for section, resume with two sections, and version fields.

- [x] **Step 2: Verify RED**

Run: `uv run pytest tests/unit/repositories/test_mappers.py -v`.

Expected: collection error because `app.repositories.mappers` does not exist.

- [x] **Step 3: Implement explicit functions**

```python
def section_to_dto(section: ResumeSection) -> ResumeSectionDTO:
    return ResumeSectionDTO(
        id=section.id,
        resume_id=section.resume_id,
        section_type=section.section_type,
        position=section.position,
        content=section.content,
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


def resume_to_dto(resume: Resume) -> ResumeDTO:
    return ResumeDTO(
        id=resume.id,
        user_id=resume.user_id,
        title=resume.title,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
        sections=tuple(section_to_dto(section) for section in resume.sections),
    )
```

Map each remaining DTO field explicitly and re-export all five functions from
`app.repositories.mappers`.

- [x] **Step 4: Verify GREEN**

Run: `uv run pytest tests/unit/repositories/test_mappers.py -v`.

Expected: PASS.

### Task 2: Полная верификация

**Files:**
- Modify: `docs/superpowers/plans/2026-07-17-orm-dto-stage-2.md`

- [x] **Step 1: Run static checks**

Run: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy app`.

Expected: each command exits with code 0.

- [x] **Step 2: Run full tests**

Run: `uv run pytest`.

Expected: all non-skipped tests pass.

- [x] **Step 3: Inspect diff**

Run: `git diff --check` and `git status --short`.

Expected: no whitespace errors; changes are limited to mappers, mapper tests and stage documentation.
