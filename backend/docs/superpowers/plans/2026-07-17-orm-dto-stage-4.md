# ORM DTO Stage 4 Implementation Plan

**Goal:** Перевести Resume CRUD на DTO без изменения HTTP API.

## Constraints

- ORM Resume и ResumeSection не покидают repository.
- PATCH сохраняет UNSET, null и value.
- Read-маппинг секций выполняется после selectinload.

### Task 1: ResumeRepository

- [ ] Написать failing tests DTO-возвратов create/read/list/update/sections.
- [ ] Перевести repository на команды, UUID и ORM→DTO мапперы.
- [ ] Проверить targeted tests.

### Task 2: ResumeService

- [ ] Написать failing tests DTO-границы сервиса.
- [ ] Убрать ORM/Pydantic imports; сохранить transactions и ownership.
- [ ] Проверить targeted tests.

### Task 3: Resume router

- [ ] Написать failing tests преобразования schemas в команды.
- [ ] Убрать ORM imports/annotations и использовать UserDTO.
- [ ] Запустить Ruff, mypy, pytest и diff check.
