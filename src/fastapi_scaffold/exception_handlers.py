import http
import traceback
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_scaffold.http_responses import http_responses, Response500
from fastapi_scaffold.responses import (
    DebugErrorResponse,
    ValidationErrorResponse,
)

from starlette.exceptions import HTTPException as StarletteHTTPException


type ExceptionHandler = Callable[[Request, Exception], Response]


async def debug_exception_handler(
        request: Request, exc: Exception
) -> JSONResponse:
    """Formats uncaught exception as 500 http response with debug info.

    Args:
        request: The FastAPI request object.
        exc: The Exception exception instance that was raised.

    Returns:
        JSONResponse 500 http response with debug info.
    """
    response = DebugErrorResponse(
        message=f"Error: {str(exc)}", traceback=traceback.format_exc()
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Formats uncaught exception as 500 http response.

    Args:
        request: The FastAPI request object.
        exc: The Exception exception instance that was raised.

    Returns:
        JSONResponse 500 http response.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Response500().model_dump(mode="json"),
    )


async def validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Formats validation error to base response format.

    Args:
        request: The FastAPI request object.
        exc: The RequestValidationError exception object that was raised.

    Returns:
        JSONResponse with 422 response and validation errors data.
    """
    response = ValidationErrorResponse(errors=exc.errors())
    return JSONResponse(
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
        content=response.model_dump(mode="json"),
    )


async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Formats exception to base http response format.

    Args:
        request: The FastAPI request object.
        exc: The StarletteHTTPException exception object that was raised.

    Returns:
        JSONResponse http response corresponding to `exc` code.
    """
    response = http_responses.get(exc.status_code, Response500)()
    if exc.detail:
        response.message = str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode="json"),
    )


def init_exc_handlers(
        app: FastAPI,
        debug: bool = False,
        exception_handler: ExceptionHandler = exception_handler,
        debug_exception_handler: ExceptionHandler = debug_exception_handler,
        http_exception_handler: ExceptionHandler = http_exception_handler,
        validation_error_handler: ExceptionHandler = (
            validation_exception_handler
        ),
) -> None:
    """Initialize exception handlers for the FastAPI application.

    Sets up handlers for:
        - HTTPException: with `Response<code>` responses,
        - RequestValidationError: with `ValidationErrorResponse` format,
        - Exception: with 500 http status (and trace if app.debug = True).

    Args:
        app: The FastAPI application instance.
    """
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(RequestValidationError)(validation_error_handler)
    if debug:
        app.exception_handler(Exception)(debug_exception_handler)
    else:
        app.exception_handler(Exception)(exception_handler)


def init_responses(
        app: FastAPI,
        validation_response: BaseModel = ValidationErrorResponse,
        internal_server_error_response: BaseModel = Response500,
) -> None:
    """Inits responses for 422 (validation) and 500 errors."""
    app.router.responses[http.HTTPStatus.UNPROCESSABLE_ENTITY] = (
        validation_response
    )
    app.router.responses[http.HTTPStatus.INTERNAL_SERVER_ERROR] = (
        internal_server_error_response
    )
