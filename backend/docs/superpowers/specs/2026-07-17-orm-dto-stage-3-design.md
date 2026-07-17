# Этап 3: User/Auth на DTO

## Цель

Исключить ORM User из AuthService, auth dependencies и auth/users routers без
изменения HTTP API, JWT и Redis-контрактов.

## Границы

`UserRepository` создаёт и запрашивает ORM внутри себя, а наружу возвращает
`UserDTO` или `UserAuthDTO` через мапперы. AuthService использует только DTO и
примитивы. `get_current_user` возвращает безопасный `UserDTO` после сохранения
проверок access type, существования пользователя, активности и token version.

## HTTP-слой

Роутер регистрации преобразует `RegisterRequest` в `CreateUserCommand`.
Роутеры refresh/logout передают сервису `refresh_token` как строку. Response
schemas и URL не меняются; `/users/me` и защищённые resume routes получают
`UserDTO` и используют его `id`.

## Безопасность

Хеш пароля доступен только через `UserAuthDTO`. Проверки JWT claim `type`, `tv`,
активности пользователя, rotation refresh token и Redis key format сохраняются.

## Проверки

Добавляются или обновляются unit/API-тесты регистрации, login, refresh, logout,
`/users/me`, неактивного пользователя, неверного типа токена и несовпадения
token version. Затем запускаются Ruff, mypy и полный pytest.
