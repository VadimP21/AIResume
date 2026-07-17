Исправляй mypy поэтапно, без изменения поведения.

Этап 1:
- missing return annotations;
- generic type arguments;
- stubs и mypy config.

Этап 2:
- заменить SQLAlchemy UUID в аннотациях на uuid.UUID.

Этап 3:
- исправить реальные несовместимости типов в auth, resume и versioning.

Этап 4:
- исправить config.py, exception handlers и оставшиеся ошибки.

После каждого этапа:
- uv run mypy app;
- uv run ruff check .;
- uv run pytest.

Не переходи к следующему этапу, пока текущие изменения не проверены.