# ORM DTO Stage 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Перевести User/Auth вертикальный срез на DTO без изменения HTTP API.

**Architecture:** Repository возвращает `UserDTO`/`UserAuthDTO`; сервис и HTTP-слой используют DTO, команды и примитивы. JWT и Redis-поведение сохраняются.

**Tech Stack:** FastAPI, SQLAlchemy async, Redis, JWT, pytest, Ruff, mypy.

## Global Constraints

- Не менять URL, request/response schemas, claims, Redis keys и БД.
- ORM User не покидает repository.
- `get_current_user` возвращает `UserDTO`.

### Task 1: Repository и AuthService

**Files:** `app/repositories/user_repository.py`, `app/services/auth_service.py`, auth service tests.

- [ ] Write failing tests for DTO returns and token flows.
- [ ] Verify RED with `uv run pytest tests/api/v1/auth tests/unit/services/test_refresh_token_rotation.py -v`.
- [ ] Make repository map users; pass `CreateUserCommand` to service; use `UserAuthDTO` for password/token checks; accept refresh token string in refresh/logout.
- [ ] Verify GREEN.

### Task 2: Dependencies и routers

**Files:** `app/api/v1/auth/dependencies.py`, `app/api/v1/auth/router.py`, `app/api/v1/users/router.py`, API tests.

- [ ] Write failing tests that current user and register handler use DTO/command.
- [ ] Verify RED.
- [ ] Return safe DTO from dependency; convert request payloads; remove model imports and ORM annotations.
- [ ] Verify GREEN.

### Task 3: Verification

- [ ] Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy app`, `uv run pytest` and `git diff --check`.
