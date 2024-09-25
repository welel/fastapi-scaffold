from http import HTTPStatus
from typing import Final, Unpack

from fastapi_scaffold.responses import BaseResponse

from pydantic import Field, create_model


type StatusCode = int


def _response_for_status_factory(status: HTTPStatus) -> BaseResponse:
    return create_model(
        f"Response{status._value_}",
        __base__=BaseResponse,
        __doc__=(
            f"""{status._value_} status response schema.

            {status.phrase} - {status.description}
            """
        ),
        success=(bool, Field(default=status.is_success)),
        message=(str, Field(default=status.phrase)),
    )


class Response200(BaseResponse):
    success: bool = HTTPStatus.OK.is_success
    message: str = HTTPStatus.OK.phrase


class Response201(BaseResponse):
    success: bool = HTTPStatus.CREATED.is_success
    message: str = HTTPStatus.CREATED.phrase


# Informational responses
Response100 = _response_for_status_factory(HTTPStatus.CONTINUE)
Response101 = _response_for_status_factory(HTTPStatus.SWITCHING_PROTOCOLS)
Response102 = _response_for_status_factory(HTTPStatus.PROCESSING)
Response103 = _response_for_status_factory(HTTPStatus.EARLY_HINTS)

# Successful responses
Response202 = _response_for_status_factory(HTTPStatus.ACCEPTED)
Response203 = _response_for_status_factory(HTTPStatus.NON_AUTHORITATIVE_INFORMATION)  # noqa: E501
Response204 = _response_for_status_factory(HTTPStatus.NO_CONTENT)
Response205 = _response_for_status_factory(HTTPStatus.RESET_CONTENT)
Response206 = _response_for_status_factory(HTTPStatus.PARTIAL_CONTENT)
Response207 = _response_for_status_factory(HTTPStatus.MULTI_STATUS)
Response208 = _response_for_status_factory(HTTPStatus.ALREADY_REPORTED)
Response226 = _response_for_status_factory(HTTPStatus.IM_USED)

# Redirection responses
Response300 = _response_for_status_factory(HTTPStatus.MULTIPLE_CHOICES)
Response301 = _response_for_status_factory(HTTPStatus.MOVED_PERMANENTLY)
Response302 = _response_for_status_factory(HTTPStatus.FOUND)
Response303 = _response_for_status_factory(HTTPStatus.SEE_OTHER)
Response304 = _response_for_status_factory(HTTPStatus.NOT_MODIFIED)
Response305 = _response_for_status_factory(HTTPStatus.USE_PROXY)
Response307 = _response_for_status_factory(HTTPStatus.TEMPORARY_REDIRECT)
Response308 = _response_for_status_factory(HTTPStatus.PERMANENT_REDIRECT)

# Client error responses
Response400 = _response_for_status_factory(HTTPStatus.BAD_REQUEST)
Response401 = _response_for_status_factory(HTTPStatus.UNAUTHORIZED)
Response402 = _response_for_status_factory(HTTPStatus.PAYMENT_REQUIRED)
Response403 = _response_for_status_factory(HTTPStatus.FORBIDDEN)
Response404 = _response_for_status_factory(HTTPStatus.NOT_FOUND)
Response405 = _response_for_status_factory(HTTPStatus.METHOD_NOT_ALLOWED)
Response406 = _response_for_status_factory(HTTPStatus.NOT_ACCEPTABLE)
Response407 = _response_for_status_factory(HTTPStatus.PROXY_AUTHENTICATION_REQUIRED)  # noqa: E501
Response408 = _response_for_status_factory(HTTPStatus.REQUEST_TIMEOUT)
Response409 = _response_for_status_factory(HTTPStatus.CONFLICT)
Response410 = _response_for_status_factory(HTTPStatus.GONE)
Response411 = _response_for_status_factory(HTTPStatus.LENGTH_REQUIRED)
Response412 = _response_for_status_factory(HTTPStatus.PRECONDITION_FAILED)
Response413 = _response_for_status_factory(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
Response414 = _response_for_status_factory(HTTPStatus.REQUEST_URI_TOO_LONG)
Response415 = _response_for_status_factory(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
Response416 = _response_for_status_factory(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)  # noqa: E501
Response417 = _response_for_status_factory(HTTPStatus.EXPECTATION_FAILED)
Response418 = _response_for_status_factory(HTTPStatus.IM_A_TEAPOT)
Response421 = _response_for_status_factory(HTTPStatus.MISDIRECTED_REQUEST)
Response422 = _response_for_status_factory(HTTPStatus.UNPROCESSABLE_ENTITY)
Response423 = _response_for_status_factory(HTTPStatus.LOCKED)
Response424 = _response_for_status_factory(HTTPStatus.FAILED_DEPENDENCY)
Response425 = _response_for_status_factory(HTTPStatus.TOO_EARLY)
Response426 = _response_for_status_factory(HTTPStatus.UPGRADE_REQUIRED)
Response428 = _response_for_status_factory(HTTPStatus.PRECONDITION_REQUIRED)
Response429 = _response_for_status_factory(HTTPStatus.TOO_MANY_REQUESTS)
Response431 = _response_for_status_factory(HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE)  # noqa: E501
Response451 = _response_for_status_factory(HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS)  # noqa: E501

# Server error responses
Response500 = _response_for_status_factory(HTTPStatus.INTERNAL_SERVER_ERROR)
Response501 = _response_for_status_factory(HTTPStatus.NOT_IMPLEMENTED)
Response502 = _response_for_status_factory(HTTPStatus.BAD_GATEWAY)
Response503 = _response_for_status_factory(HTTPStatus.SERVICE_UNAVAILABLE)
Response504 = _response_for_status_factory(HTTPStatus.GATEWAY_TIMEOUT)
Response505 = _response_for_status_factory(HTTPStatus.HTTP_VERSION_NOT_SUPPORTED)  # noqa: E501
Response506 = _response_for_status_factory(HTTPStatus.VARIANT_ALSO_NEGOTIATES)
Response507 = _response_for_status_factory(HTTPStatus.INSUFFICIENT_STORAGE)
Response508 = _response_for_status_factory(HTTPStatus.LOOP_DETECTED)
Response510 = _response_for_status_factory(HTTPStatus.NOT_EXTENDED)
Response511 = _response_for_status_factory(HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED)  # noqa: E501


def _gather_http_responses() -> dict[StatusCode, BaseResponse]:
    responses = {}

    response_prefix = "Response"
    for var_name, var_value in globals().items():
        if var_name.startswith(response_prefix):

            postfix = var_name[len(response_prefix):]
            if not postfix.isdigit() or len(postfix) != 3:
                continue

            code = int(postfix)
            responses[code] = var_value
    return responses


http_responses: Final = _gather_http_responses()


def responses_for_codes(
        *codes: Unpack[tuple[StatusCode]]
) -> dict[StatusCode, dict[str, BaseResponse]]:
    """Gets http responses for HTTP status codes.

    Args:
        *codes: A tuple of http status codes to return schema for.

    Returns:
        Returns http responses as FastAPI responses argument.
    """
    responses = {}
    for code in sorted(codes):
        response = http_responses.get(code, BaseResponse)
        responses[code] = {"model": response}
    return responses
