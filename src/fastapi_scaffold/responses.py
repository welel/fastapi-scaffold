from typing import Iterable, Self, Sequence, Type

from pydantic import BaseModel, ConfigDict, create_model
from pydantic_core import ErrorDetails

from fastapi_scaffold.pagination import PaginationParams, PaginationSchema


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseResponse(Schema):
    """Base API response schema.

    All app responses must inherit from this schema.
    """
    success: bool = True
    message: str = ""


class ErrorResponse(BaseResponse):
    success: bool = False
    message: str = "Error"


class ValidationErrorResponse(ErrorResponse):
    """Pydantic validation error schema."""
    message: str = "Validation error"
    errors: list[ErrorDetails]


class DebugErrorResponse(ErrorResponse):
    traceback: str


class DataResponse[Data](BaseResponse):
    """Base data response schema.

    All responses with business logic data must inherit from this schema.
    Data must be placed at `data` field.
    """
    success: bool = True
    message: str = "Data retrieved successfully"
    data: Data

    @classmethod
    def single_by_key(cls, key: str, schema: BaseModel | Type) -> Self:
        """Generates schema with single object in `data` placed by `key`."""
        data_model = create_model(schema.__name__, **{key: (schema, ...)})
        return cls[data_model]


class ListData[ListItem](BaseModel):
    list: Sequence[ListItem]


class ListResponse[ListItem](DataResponse[ListItem]):
    """Base data response schema.

    All responses with business logic data as list with pagination
    must inherit from this schema.
    List must be placed at `data` -> `list` field.
    """
    data: ListData[ListItem]
    pagination: PaginationSchema

    @staticmethod
    def _get_list_elements_type[T](items: Iterable[T]) -> type[T] | None:
        """Returns type of first sequence element."""
        for item in items:
            return type(item)

    @classmethod
    def from_list(
        cls,
        items: Sequence[ListItem],
        total_count: int,
        params: PaginationParams,
        response_message: str | None,
    ) -> Self:
        """Generates paginated list response.

        Args:
            items: Items to place at `data` -> `list`.
            total_count: Total items for pagination.
            params: Pagination params.
            response_message: Overrides base response `message`.

        Returns:
            ListResponse with items and calculated pagination.
        """
        message_kwarg = {}
        if response_message is not None:
            message_kwarg = {"message": response_message}
        return cls(
            data=ListData[cls._get_list_elements_type(items)](list=items),
            pagination=PaginationSchema.from_params(params, total_count),
            **message_kwarg,
        )
