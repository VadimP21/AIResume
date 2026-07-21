"""Содержит общие типы внутренних DTO."""

from typing import Final


class UnsetType:
    """Обозначает поле, не переданное при частичном обновлении."""

    __slots__ = ()

    def __repr__(self) -> str:
        """Возвращает строковое представление маркера."""
        return "UNSET"


UNSET: Final = UnsetType()
