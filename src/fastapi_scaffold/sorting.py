from enum import StrEnum
from typing import NamedTuple, Unpack

from fastapi import Query


class SortParams(NamedTuple):
    sort_by: str
    order_by: str


class SortOrderOptions(StrEnum):
    asc = "asc"
    desc = "desc"


def get_sort_params(
        *sort_options: Unpack[tuple[str]],
        default: str | None = None,
) -> SortParams:
    try:
        default = default or next(iter(sort_options))
    except StopIteration:
        default = None
    options_str = "_".join(sort_options)
    options_dict = {op: op for op in sort_options}
    sort_options_enum = StrEnum(f"SortOptions_{options_str}", options_dict)

    def _get_sort_params(
            sort_by: sort_options_enum | None = Query(  # type: ignore
                default, description="Sort by field"
            ),
            order_by: SortOrderOptions = Query(
                SortOrderOptions.desc, description="Sort order"
            ),
    ):
        return SortParams(sort_by=sort_by, order_by=order_by)
    return _get_sort_params
