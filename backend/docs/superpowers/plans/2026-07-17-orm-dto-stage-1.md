# ORM DTO Stage 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать независимый пакет неизменяемых DTO и команд для последующей изоляции ORM.

**Architecture:** DTO располагаются в `app/dto` и используют только стандартную библиотеку. `UNSET` в `common.py` сохраняет семантику PATCH; DTO разделены по пользовательской, resume и versioning областям. Существующие маршруты, ORM и схемы не изменяются.

**Tech Stack:** Python 3.14, dataclasses, pytest, Ruff, mypy.

## Global Constraints

- Не изменять HTTP-контракты, response schemas, ORM-модели и схему PostgreSQL.
- DTO не импортируют SQLAlchemy, FastAPI или Pydantic HTTP-схемы.
- Все DTO и команды: `@dataclass(frozen=True, slots=True)`.
- `UserDTO` не содержит хеш пароля; он допускается только в `UserAuthDTO`.
- Не перезаписывать незакоммиченные изменения пользователя.
- Git-коммит не входит в задачу и не создаётся без отдельного запроса.

---

### Task 1: Контракт DTO и `UNSET`

**Files:**
- Create: `tests/unit/dto/test_contracts.py`
- Create: `app/dto/common.py`
- Create: `app/dto/users.py`
- Create: `app/dto/resumes.py`
- Create: `app/dto/versions.py`
- Create: `app/dto/__init__.py`

**Interfaces:**
- Produces: `UNSET`, `CreateUserCommand`, `UserDTO`, `UserAuthDTO`, `SectionType`, `CreateResumeCommand`, `UpdateResumeCommand`, `CreateSectionCommand`, `UpdateSectionCommand`, `ResumeDTO`, `ResumeSectionDTO`, `ResumeVersionDTO`.

- [x] **Step 1: Write the failing test**

```python
from app.dto import UNSET, UpdateResumeCommand


def test_update_command_distinguishes_unset_none_and_value() -> None:
    assert UpdateResumeCommand().title is UNSET
    assert UpdateResumeCommand(title=None).title is None
    assert UpdateResumeCommand(title="Senior Python Developer").title == "Senior Python Developer"
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/dto/test_contracts.py -v`

Expected: collection error because `app.dto` does not exist.

- [x] **Step 3: Write minimal implementation**

```python
# app/dto/common.py
class _Unset:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNSET"


UNSET = _Unset()
```

```python
# app/dto/resumes.py
@dataclass(frozen=True, slots=True)
class UpdateResumeCommand:
    title: str | None | _Unset = UNSET
```

Implement the complete public contract:

```python
@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: UUID
    email: str
    is_active: bool
    token_version: int


@dataclass(frozen=True, slots=True)
class UserAuthDTO:
    id: UUID
    email: str
    password_hash: str
    is_active: bool
    token_version: int


@dataclass(frozen=True, slots=True)
class CreateResumeCommand:
    title: str


@dataclass(frozen=True, slots=True)
class CreateSectionCommand:
    section_type: SectionType
    content: dict[str, Any]


@dataclass(frozen=True, slots=True)
class UpdateSectionCommand:
    content: dict[str, Any] | None | _Unset = UNSET


@dataclass(frozen=True, slots=True)
class ResumeSectionDTO:
    id: UUID
    resume_id: UUID
    section_type: SectionType
    position: int
    content: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ResumeDTO:
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    sections: tuple[ResumeSectionDTO, ...]


@dataclass(frozen=True, slots=True)
class ResumeVersionDTO:
    id: UUID
    resume_id: UUID
    snapshot: dict[str, object]
    created_at: datetime
```

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/dto/test_contracts.py -v`

Expected: PASS.

### Task 2: Изоляция и неизменяемость DTO

**Files:**
- Modify: `tests/unit/dto/test_contracts.py`
- Modify: `app/dto/__init__.py`

**Interfaces:**
- Consumes: публичные символы из `app.dto`.
- Produces: тестируемый публичный DTO API без инфраструктурных импортов.

- [x] **Step 1: Write the failing tests**

```python
from dataclasses import FrozenInstanceError

import pytest

from app.dto import UserDTO


def test_user_dto_is_immutable() -> None:
    user = UserDTO(id=uuid4(), email="user@example.com", is_active=True, token_version=0)
    with pytest.raises(FrozenInstanceError):
        user.email = "other@example.com"  # type: ignore[misc]
```

Add assertions that source files under `app/dto` do not contain imports whose
module begins with `sqlalchemy`, `fastapi`, `pydantic` or `app.models`.

- [x] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/dto/test_contracts.py -v`

Expected: FAIL until DTO decorators and package exports are implemented.

- [x] **Step 3: Implement exports and frozen/slotted DTOs**

```python
# app/dto/__init__.py
from app.dto.common import UNSET, UnsetType
from app.dto.resumes import (
    CreateResumeCommand,
    CreateSectionCommand,
    ResumeDTO,
    ResumeSectionDTO,
    SectionType,
    UpdateResumeCommand,
    UpdateSectionCommand,
)
from app.dto.users import CreateUserCommand, UserAuthDTO, UserDTO
from app.dto.versions import ResumeVersionDTO
```

Use only standard-library imports inside all DTO modules.

- [x] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/dto/test_contracts.py -v`

Expected: PASS.

### Task 3: Полная проверка этапа

**Files:**
- Modify: `docs/superpowers/plans/2026-07-17-orm-dto-stage-1.md` — отметить выполненные шаги только после получения результатов.

- [x] **Step 1: Run static checks**

Run: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy app`.

Expected: all commands exit with code 0.

- [x] **Step 2: Run full tests**

Run: `uv run pytest`.

Expected: all non-skipped tests pass.

- [x] **Step 3: Inspect final diff**

Run: `git diff --check` and `git status --short`.

Expected: no whitespace errors; only DTO, DTO-test and planning/specification changes are attributed to this task.
