from fastapi import FastAPI

from fastapi_scaffold.exception_handlers import (
    init_exc_handlers,
    init_responses,
)
from fastapi_scaffold.http_responses import (  # noqa: F401
    Response200,
    Response201,
)
from fastapi_scaffold.pagination import (  # noqa: F401
    PaginationParamsQuery,
    paginate,
)
from fastapi_scaffold.responses import (  # noqa: F401
    BaseResponse,
    DataResponse,
    ErrorResponse,
    ListResponse,
    Schema,
)
from fastapi_scaffold.sorting import get_sort_params, sort  # noqa: F401


class FastAPIScaffold:
    """Fast API scaffold library.

    Handles:
        - Schemas
        - Error handlers
        - Query helpers
    """

    def __init__(self, app: FastAPI, debug: bool = False):
        init_responses(app)
        init_exc_handlers(app, debug=debug)
