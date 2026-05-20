# 008. Формирование snapshot версии обращается к несуществующему полю секции

- **Серьёзность:** Medium
- **Статус:** Open
- **Затронутые файлы:** `app/services/versioning.py:24-32`, `app/models/resume_section.py:35-60`

## Описание

`VersioningService.create_snapshot()` читает `section.type`, тогда как в `ResumeSection` определено поле `section_type`.

## Влияние

При создании snapshot для резюме с секциями будет выброшен `AttributeError`; версия не сохранится.

## Рекомендуемое решение

Использовать `section.section_type.value` и покрыть создание snapshot резюме с каждой поддерживаемой секцией тестом.
