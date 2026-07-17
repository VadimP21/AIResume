# Этап 4: Resume CRUD на DTO

## Цель

Изолировать ORM-модели Resume и ResumeSection внутри ResumeRepository, сохранив
HTTP API, ownership-проверки, транзакции и eager loading секций.

## Границы

Repository принимает UUID и DTO-команды, а возвращает `ResumeDTO` и
`ResumeSectionDTO` через мапперы. Service использует UUID и DTO, не импортирует
ORM и HTTP-схемы. Router преобразует Pydantic schemas в DTO-команды и строит
ответы из DTO.

## PATCH

Router формирует update-команды с учётом `model_fields_set`, сохраняя различие
между отсутствующим полем, `null` и значением. Repository применяет только поля,
не равные `UNSET`.

## Загрузка

Все возвращаемые `ResumeDTO` с секциями строятся после `selectinload`.
Мапперы не выполняют запросов и не допускают lazy loading после repository.

## Ограничения

Не менять БД, URL, response schemas, ownership и транзакционные границы.
Import/export/versioning остаются для следующих этапов.
