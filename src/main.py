from fastapi import Depends, FastAPI
from pydantic import Field

from fastapi_scaffold.http_responses import responses_for_codes
from fastapi_scaffold.exception_handlers import (
    init_exc_handlers,
    init_responses,
)
from fastapi_scaffold.responses import (
    DataResponse,
    ListResponse,
    Schema,
    ValidationErrorResponse,
)
from fastapi_scaffold.pagination import PaginationParamsQuery
from fastapi_scaffold.sorting import get_sort_params, SortParams


DEBUG = True


app = FastAPI(
    # responses={
    #     422: {"model": ValidationErrorResponse},
    #     **responses_for_codes(500),
    # }
)

init_responses(app)
init_exc_handlers(app, debug=DEBUG)


class User(Schema):
    name: str
    age: int = Field(..., ge=0)


@app.post("/users/", response_model=DataResponse.single_by_key("user", User))
def create_user_(user: User):
    return DataResponse(data={"user": user})


"""Generates swagger:

{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "user": {
      "name": "string",
      "age": 0
    }
  }
}
"""


@app.get(
        "/users/",
        response_model=ListResponse[User],
        responses=responses_for_codes(400, 500),
)
def get_user_list_(
    pagination: PaginationParamsQuery,
    sort: SortParams = Depends(get_sort_params("name", "age")),
):
    users = [User(name="Name", age=20), User(name="Name 2", age=22)]
    total_count = 12

    # Response generation
    return ListResponse[User].from_list(
        users, total_count, pagination, "Custom response message"
    )


"""Generates swagger:

{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "list": [
      {
        "name": "string",
        "age": 0
      }
    ]
  },
  "pagination": {
    "total_items": 5,
    "page": 1,
    "per_page": 1,
    "next_page": 2,
    "prev_page": null,
    "total_pages": 5
  }
}
"""


@app.post(
        "/users-with-error/",
        response_model=DataResponse.single_by_key("user", User),
)
def create_user_with_error_(user: User):
    raise Exception("Some error")
    return DataResponse(data={"user": user})
