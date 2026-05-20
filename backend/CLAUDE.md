# CLAUDE.md

# AIResume Backend Development Guide

Этот документ описывает целевую архитектуру, соглашения и технические границы проекта.
Обязательные правила работы агента находятся в `AGENTS.md`, а пошаговые процессы —
в `docs/workflows/`.

---

# Project Goal

AIResume is a backend service for resume management.

Current responsibilities:

- User authentication
- Resume CRUD
- Resume sections
- Resume rendering (planned)
- Resume versioning (planned)
- AI integration (planned)

---

# Technology Stack

Language

- Python >=3.12
- Целевая версия разработки: Python 3.14

Framework

- FastAPI

Database

- PostgreSQL 16

ORM

- SQLAlchemy 2.x Async

Cache

- Redis

Authentication

- JWT
- Argon2

Migrations

- Alembic

Background jobs

- Celery

Validation

- Pydantic v2

Testing

- pytest

Formatting

- Ruff

Containerization

- Docker

---

# Project Structure

app/

    main.py
    main_offline.py

    api/
        routers
        dependencies

    services/

    repositories/

    models/

    schemas/

    db/

    middleware/

    middeleware/  # legacy directory; do not add new modules here

    core/

    tasks/

static/

storage/

Architecture:

```
Router
    ↓
Service
    ↓
Repository
    ↓
Database
```

---

# Layer Responsibilities

## Router

Responsibilities

- HTTP
- validation
- dependency injection
- response models

Must NOT contain

- SQL
- business logic

---

## Service

Responsibilities

- business logic
- transactions
- orchestration

Can call

- repositories
- Redis
- external APIs

Should NOT

- write SQL

---

## Repository

Responsibilities

- database access only

Should contain

- select
- insert
- update
- delete

Should NOT contain

- business rules

---

# Dependency Injection

Dependencies should be created using FastAPI Depends.

Preferred flow:

```
Router
↓

Depends(get_service)

↓

Service(repository)

↓

Repository(session)
```

---

# Database Conventions

Primary keys

- UUID

Timestamps

- created_at
- updated_at

Transactions belong to Service layer.

Repository never calls commit().

Preferred pattern:

```
create()

flush()

refresh()

commit()
```

Only Service manages transaction boundaries.

---

# SQLAlchemy

Always use

- select()
- AsyncSession
- scalar()
- scalars()

Prefer

- selectinload()
- joinedload()

Avoid

- lazy loading in API responses
- N+1 queries

---

# Pydantic

Use Pydantic v2.

Always

- validate input
- return DTOs

Never return ORM objects directly.

---

# Error Handling

Сервисы должны поднимать доменные исключения, а HTTP-слой или централизованный
handler — преобразовывать их в HTTP-ответы.

Avoid

- HTTPException inside Service
- swallowing exceptions

Стандартное соответствие ошибок:

| Сценарий | HTTP-статус |
| --- | --- |
| Ошибка валидации входных данных | 422 |
| Неаутентифицированный запрос | 401 |
| Недостаточно прав | 403 |
| Ресурс не найден | 404 |
| Конфликт уникальности или состояния | 409 |
| Непредвиденная ошибка | 500 |

---

# Authentication

Authentication flow

```
JWT Access

↓

JWT Validation

↓

Current User

↓

Business Logic
```

Refresh tokens

- stored in Redis

Passwords

- Argon2

Never store

- plaintext passwords
- plaintext refresh tokens

Перед выпуском в production проверить:

- debug и test endpoint не подключены к публичным маршрутам;
- access JWT и refresh JWT проверяются как разные типы токенов;
- CORS, Trusted Hosts и секреты соответствуют окружению.

---

# Redis

Redis is used for

- refresh tokens
- cache (future)
- Celery broker

Avoid business logic inside Redis helpers.

---

# Celery

Background tasks should

- be idempotent
- have retries
- log failures

---

# Logging

Use structured logging.

Every request should have

- request_id

Log

- errors
- execution time

Never log

- passwords
- JWT
- secrets

---

# API Style

Use

/api/v1/

Status codes

200

201

204

400

401

403

404

422

500

---

# Testing

Project uses

pytest

Preferred structure

tests/

    unit/

    integration/

Each feature should have

- happy path
- validation
- authorization
- edge cases

Тесты должны запускаться через `uv run pytest`. Для изменений, затрагивающих БД,
использовать изолированную тестовую БД и применять миграции в ней.

---

# Code Style

Prefer

small functions

clear names

composition

explicit typing

Avoid

large classes

deep nesting

duplicated code

---

# Performance Checklist

Before merging check

- indexes
- N+1
- pagination
- query count
- unnecessary serialization

---

# Security Checklist

Always verify

- JWT validation
- authorization
- SQL Injection
- secrets
- password hashing

---

# Review Checklist

When reviewing code inspect

Architecture

Business logic

Transactions

Concurrency

Performance

Security

Tests

Readability

Maintainability

---

# Known Technical Debt

Подтверждённые проблемы ведутся отдельными карточками в `docs/backlog/`.
Не дублировать их содержание в этом документе. При исправлении обновлять статус
соответствующей карточки.

## Known deviations from target architecture

Текущие отклонения и технический долг перечислены в карточках `001`–`010` в
`docs/backlog/`. Они не делают целевые правила выше неактуальными: сначала
исправляется реализация, затем обновляется статус карточки.

---

# Workflow

Использовать соответствующий сценарий:

- `docs/workflows/development.md` — разработка;
- `docs/workflows/testing.md` — тестирование;
- `docs/workflows/migrations.md` — миграции;
- `docs/workflows/code-review.md` — code review.
- `docs/workflows/commits.md` — создание Git-коммитов.

---

# Principles

Prefer readability over cleverness.

Prefer explicit code over magic.

Prefer maintainability over micro-optimizations.

Do not introduce new dependencies unless necessary.

Minimize changes outside the requested scope.

Always preserve backward compatibility unless explicitly instructed otherwise.
