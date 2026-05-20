# 001. Refresh JWT принимается как access JWT

- **Серьёзность:** High
- **Статус:** Resolved
- **Затронутые файлы:** `app/api/v1/auth/dependencies.py`, `app/core/security.py`, `tests/api/v1/auth/test_dependencies.py`

## Описание

`get_current_user()` проверяет подпись, срок действия и версию токена, но не claim `type`. Поэтому refresh JWT с `type="refresh"` принимается в заголовке `Authorization: Bearer` всеми защищёнными endpoint.

## Влияние

Refresh JWT с более длительным сроком действия получает доступ к API как access JWT. Нарушается разделение типов токенов и увеличивается период доступа при компрометации refresh JWT.

## Рекомендуемое решение

В `get_current_user()` отклонять токен, если `payload.get("type") != "access"`; добавить тесты для access и refresh JWT на защищённом endpoint.

## Решение

В `get_current_user()` добавлена обязательная проверка claim `type` до загрузки пользователя. Защищённые endpoint принимают только access JWT; refresh JWT отклоняется с HTTP 401. Добавлены регрессионные тесты обоих сценариев.
