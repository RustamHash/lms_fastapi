"""Кастомные исключения API."""

from __future__ import annotations

from fastapi import HTTPException, status


class APIError(HTTPException):
    """Базовая ошибка API."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "Внутренняя ошибка сервера") -> None:
        super().__init__(status_code=self.status_code, detail=message)


class BadRequestError(APIError):
    """Некорректный запрос."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str = "Некорректный запрос") -> None:
        super().__init__(message)


class UnauthorizedError(APIError):
    """Не авторизован."""

    status_code: int = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message: str = "Не авторизован") -> None:
        super().__init__(message)


class ForbiddenError(APIError):
    """Доступ запрещен."""

    status_code: int = status.HTTP_403_FORBIDDEN

    def __init__(self, message: str = "Доступ запрещен") -> None:
        super().__init__(message)


class NotFoundError(APIError):
    """Ресурс не найден."""

    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, message: str = "Ресурс не найден") -> None:
        super().__init__(message)


class ConflictError(APIError):
    """Конфликт данных."""

    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, message: str = "Конфликт данных") -> None:
        super().__init__(message)
