from typing import Self, Sequence

from pydantic import BaseModel, ConfigDict, create_model
from pydantic_core import ErrorDetails

from .pagination import PaginationParams, PaginationSchema


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseResponse(Schema):
    success: bool = True
    message: str = ""


class ErrorResponse(BaseResponse):
    success: bool = False
    message: str = "Error"


class ValidationErrorResponse(ErrorResponse):
    message: str = "Validation error"
    errors: list[ErrorDetails]


class DebugErrorResponse(ErrorResponse):
    traceback: str


class DataResponse[Data](BaseResponse):
    success: bool = True
    message: str = "Data retrieved successfully"
    data: Data

    @classmethod
    def single_by_key(cls, key: str, schema: BaseModel) -> Self:
        data_model = create_model(schema.__name__, **{key: (schema, ...)})
        return cls[data_model]


class ListData[ListItem](BaseModel):
    list: Sequence[ListItem]


class ListResponse[ListItem](DataResponse[ListItem]):
    data: ListData[ListItem]
    pagination: PaginationSchema

    @staticmethod
    def _get_list_elements_type[T](items: list[T]) -> type[T] | None:
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
        message_kwarg = {}
        if response_message is not None:
            message_kwarg = {"message": response_message}
        return cls(
            data=ListData[cls._get_list_elements_type(items)](list=items),
            pagination=PaginationSchema.from_params(params, total_count),
            **message_kwarg,
        )
