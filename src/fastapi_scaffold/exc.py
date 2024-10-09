from collections.abc import Sequence
from enum import StrEnum
from http import HTTPStatus

from fastapi.exceptions import RequestValidationError
from pydantic_core import ErrorDetails as PydanticErrorDetails
from pydantic_core import InitErrorDetails, PydanticCustomError
from pydantic_core import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException


class ScaffoldException(HTTPException):
    """Base exception class for all errors raised by Scaffold.

    A custom exception handler for FastAPI takes care
    of catching and returning a proper HTTP error from them.

    Args:
        message: The error message that'll be displayed to the user.
        status_code: The status code of the HTTP response. Defaults to 500.
        headers: Additional headers to be included in the response.
    """

    def __init__(
        self,
        message: str,
        status_code: int | HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=message,
            headers=headers,
        )
        self.message = message


class BadRequest(ScaffoldException):
    def __init__(
            self,
            message: str = "Bad request",
            status_code: int | HTTPStatus = HTTPStatus.BAD_REQUEST,
            headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message, status_code, headers)


class Unauthorized(ScaffoldException):
    def __init__(
            self,
            message: str = "Unauthorized",
            status_code: int | HTTPStatus = HTTPStatus.UNAUTHORIZED,
            headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message, status_code, headers)


class Forbidden(ScaffoldException):
    def __init__(
            self,
            message: str = "Forbidden",
            status_code: int | HTTPStatus = HTTPStatus.FORBIDDEN,
            headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message, status_code, headers)


class ResourceNotFound(ScaffoldException):
    def __init__(
            self,
            message: str = "Not Found",
            status_code: int | HTTPStatus = HTTPStatus.NOT_FOUND,
            headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message, status_code, headers)


class ResourceAlreadyExists(ScaffoldException):
    def __init__(
            self,
            message: str = "Already exists",
            status_code: int | HTTPStatus = HTTPStatus.CONFLICT,
            headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message, status_code, headers)


class InternalServerError(ScaffoldException):
    def __init__(
            self,
            message: str = "Internal Server Error",
            status_code: int | HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
            headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message, status_code, headers)


class ErrorType(StrEnum):
    """Pydantic type error.

    May extend if needed with custom or pydantic values from
    `pydantic_core.core_schema.ErrorType`.
    """
    missing = "missing"
    value_error = "value_error"


class ErrorDetails(PydanticErrorDetails):
    """Pydantic validation error details."""
    Type = ErrorType


class ValidationError(RequestValidationError):
    """Pydantic-style validation error.

    Args:
        errors (Sequence[ErrorDetails]): Pydantic errors.
    """
    def __init__(self, errors: Sequence[ErrorDetails]) -> None:
        self._errors = errors

    def errors(self) -> list[ErrorDetails]:
        pydantic_errors: list[InitErrorDetails] = []
        for error in self._errors:
            if (ctx := error.get("ctx")) is not None:
                type_ = PydanticCustomError(error["type"], error["msg"], ctx)
            else:
                type_ = PydanticCustomError(error["type"], error["msg"])

            pydantic_errors.append(
                InitErrorDetails(
                    type=type_,
                    loc=error["loc"],
                    input=error["input"],
                )
            )
        pydantic_error = PydanticValidationError.from_exception_data(
            self.__class__.__name__, pydantic_errors
        )
        return pydantic_error.errors()
