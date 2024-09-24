import math
from typing import Annotated, NamedTuple, Self

from fastapi import Depends, Query
from pydantic import BaseModel, Field


class PaginationParams(NamedTuple):
    page: int
    per_page: int


def get_pagination_params(
    page: int = Query(
        1,
        description="Current page number",
        ge=1,
        examples=[1],
    ),
    per_page: int = Query(
        10,
        description="Number of items to get on a page",
        ge=1,
        examples=[10],
    )
):
    return PaginationParams(page=page, per_page=per_page)


PaginationParamsQuery = Annotated[
    PaginationParams, Depends(get_pagination_params)
]
"""Pagination query parameters - `page`, `per_page`."""


class PaginationSchema(BaseModel):
    """Pagination data schema."""

    total_items: int = Field(
        ...,
        description="Total number of elements (must be positive)",
        ge=0,
        examples=[5],
    )
    page: int = Field(
        ...,
        description="Current page (must be at least 1)",
        ge=1,
        examples=[1],
    )
    per_page: int = Field(
        ...,
        description="Number of items per page (must be positive)",
        ge=1,
        examples=[1],
    )
    next_page: int | None = Field(
        None,
        description="Number of the next page (can be None)",
        examples=[2],
    )
    prev_page: int | None = Field(
        None,
        description="Number of the previous page (can be None)",
        examples=[None],
    )
    total_pages: int = Field(
        ...,
        description="Number of total pages (must be positive)",
        ge=0,
        examples=[5],
    )

    @classmethod
    def from_params(
            cls, params: PaginationParams, total: int
    ) -> Self:
        """Create instance from pagination params and total items count.

        Args:
            params: Pagination params.
            total: A total number of items available for the pagination.

        Returns:
            The schema instance with calculated fields.
        """
        is_last_page = params.page * params.per_page >= total
        return cls(
            total_items=total,
            page=params.page,
            per_page=params.per_page,
            next_page=params.page + 1 if not is_last_page else None,
            prev_page=params.page - 1 if params.page > 1 else None,
            total_pages=math.ceil(total / params.per_page),
        )
