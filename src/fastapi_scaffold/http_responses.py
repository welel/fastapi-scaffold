from http import HTTPStatus
from typing import Unpack

from pydantic import Field, create_model

from .responses import BaseResponse


type StatusCode = int


def response_for_status_factory(status: HTTPStatus) -> BaseResponse:
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
Response100 = response_for_status_factory(HTTPStatus.CONTINUE)
Response101 = response_for_status_factory(HTTPStatus.SWITCHING_PROTOCOLS)
Response102 = response_for_status_factory(HTTPStatus.PROCESSING)
Response103 = response_for_status_factory(HTTPStatus.EARLY_HINTS)

# Successful responses
Response202 = response_for_status_factory(HTTPStatus.ACCEPTED)
Response203 = response_for_status_factory(HTTPStatus.NON_AUTHORITATIVE_INFORMATION)  # noqa: E501
Response204 = response_for_status_factory(HTTPStatus.NO_CONTENT)
Response205 = response_for_status_factory(HTTPStatus.RESET_CONTENT)
Response206 = response_for_status_factory(HTTPStatus.PARTIAL_CONTENT)
Response207 = response_for_status_factory(HTTPStatus.MULTI_STATUS)
Response208 = response_for_status_factory(HTTPStatus.ALREADY_REPORTED)
Response226 = response_for_status_factory(HTTPStatus.IM_USED)

# Redirection responses
Response300 = response_for_status_factory(HTTPStatus.MULTIPLE_CHOICES)
Response301 = response_for_status_factory(HTTPStatus.MOVED_PERMANENTLY)
Response302 = response_for_status_factory(HTTPStatus.FOUND)
Response303 = response_for_status_factory(HTTPStatus.SEE_OTHER)
Response304 = response_for_status_factory(HTTPStatus.NOT_MODIFIED)
Response305 = response_for_status_factory(HTTPStatus.USE_PROXY)
Response307 = response_for_status_factory(HTTPStatus.TEMPORARY_REDIRECT)
Response308 = response_for_status_factory(HTTPStatus.PERMANENT_REDIRECT)

# Client error responses
Response400 = response_for_status_factory(HTTPStatus.BAD_REQUEST)
Response401 = response_for_status_factory(HTTPStatus.UNAUTHORIZED)
Response402 = response_for_status_factory(HTTPStatus.PAYMENT_REQUIRED)
Response403 = response_for_status_factory(HTTPStatus.FORBIDDEN)
Response404 = response_for_status_factory(HTTPStatus.NOT_FOUND)
Response405 = response_for_status_factory(HTTPStatus.METHOD_NOT_ALLOWED)
Response406 = response_for_status_factory(HTTPStatus.NOT_ACCEPTABLE)
Response407 = response_for_status_factory(HTTPStatus.PROXY_AUTHENTICATION_REQUIRED)  # noqa: E501
Response408 = response_for_status_factory(HTTPStatus.REQUEST_TIMEOUT)
Response409 = response_for_status_factory(HTTPStatus.CONFLICT)
Response410 = response_for_status_factory(HTTPStatus.GONE)
Response411 = response_for_status_factory(HTTPStatus.LENGTH_REQUIRED)
Response412 = response_for_status_factory(HTTPStatus.PRECONDITION_FAILED)
Response413 = response_for_status_factory(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
Response414 = response_for_status_factory(HTTPStatus.REQUEST_URI_TOO_LONG)
Response415 = response_for_status_factory(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
Response416 = response_for_status_factory(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)  # noqa: E501
Response417 = response_for_status_factory(HTTPStatus.EXPECTATION_FAILED)
Response418 = response_for_status_factory(HTTPStatus.IM_A_TEAPOT)
Response421 = response_for_status_factory(HTTPStatus.MISDIRECTED_REQUEST)
Response422 = response_for_status_factory(HTTPStatus.UNPROCESSABLE_ENTITY)
Response423 = response_for_status_factory(HTTPStatus.LOCKED)
Response424 = response_for_status_factory(HTTPStatus.FAILED_DEPENDENCY)
Response425 = response_for_status_factory(HTTPStatus.TOO_EARLY)
Response426 = response_for_status_factory(HTTPStatus.UPGRADE_REQUIRED)
Response428 = response_for_status_factory(HTTPStatus.PRECONDITION_REQUIRED)
Response429 = response_for_status_factory(HTTPStatus.TOO_MANY_REQUESTS)
Response431 = response_for_status_factory(HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE)  # noqa: E501
Response451 = response_for_status_factory(HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS)  # noqa: E501

# Server error responses
Response500 = response_for_status_factory(HTTPStatus.INTERNAL_SERVER_ERROR)
Response501 = response_for_status_factory(HTTPStatus.NOT_IMPLEMENTED)
Response502 = response_for_status_factory(HTTPStatus.BAD_GATEWAY)
Response503 = response_for_status_factory(HTTPStatus.SERVICE_UNAVAILABLE)
Response504 = response_for_status_factory(HTTPStatus.GATEWAY_TIMEOUT)
Response505 = response_for_status_factory(HTTPStatus.HTTP_VERSION_NOT_SUPPORTED)  # noqa: E501
Response506 = response_for_status_factory(HTTPStatus.VARIANT_ALSO_NEGOTIATES)
Response507 = response_for_status_factory(HTTPStatus.INSUFFICIENT_STORAGE)
Response508 = response_for_status_factory(HTTPStatus.LOOP_DETECTED)
Response510 = response_for_status_factory(HTTPStatus.NOT_EXTENDED)
Response511 = response_for_status_factory(HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED)  # noqa: E501


def gather_http_responses() -> dict[StatusCode, BaseResponse]:
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


http_responses = gather_http_responses()


def responses_for_codes(
        *codes: Unpack[tuple[StatusCode]]
) -> dict[StatusCode, dict[str, BaseResponse]]:
    responses = {}
    for code in sorted(codes):
        response = http_responses.get(code, BaseResponse)
        responses[code] = {"model": response}
    return responses
