# 003. Удаление резюме откатывается при закрытии сессии

- **Серьёзность:** High
- **Статус:** Resolved
- **Затронутые файлы:** `app/services/resume.py`, `tests/unit/services/test_resume_service.py`, `tests/integration/services/test_resume_delete.py`, `docs/workflows/testing.md`

## Описание

`ResumeService.delete_resume()` вызывает `delete()` и `flush()`, но не выполняет `commit()`. Dependency `get_db()` закрывает сессию после ответа, поэтому незавершённая транзакция откатывается.

## Влияние

`DELETE /api/v1/resumes/{resume_id}` отвечает `204`, но запись остаётся в PostgreSQL.

## Рекомендуемое решение

Управлять транзакцией в service: после удаления выполнить `commit()`, а при исключении — `rollback()`; добавить интеграционный тест, который повторно читает удалённое резюме в новой сессии.

## Решение

`ResumeService.delete_resume()` завершает удаление через `commit()` и выполняет `rollback()` при ошибке. Поиск резюме использует именованные аргументы `resume_id` и `user_id`, исключая их перестановку в delete-flow. Добавлены unit-тесты границы транзакции и PostgreSQL integration-тест с проверкой результата в новой сессии.
