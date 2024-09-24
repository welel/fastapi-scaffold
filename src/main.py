import http
from fastapi import Depends, FastAPI, HTTPException, APIRouter
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
)
from fastapi_scaffold.pagination import PaginationParamsQuery
from fastapi_scaffold.sorting import get_sort_params, SortParams


DEBUG = True

app = FastAPI()

init_responses(app)
init_exc_handlers(app, debug=DEBUG)


class User(Schema):
    name: str
    age: int = Field(..., ge=0)


class Address(Schema):
    country: str
    city: str


class UserData(Schema):
    user: User
    address: Address


@app.get(
          "/users/{user_id}",
          response_model=DataResponse[UserData],
)
def get_user_(user_id: int):
    user = User(name=f"Name {user_id}", age=22)
    address = Address(country="Russia", city="Sochi")
    return DataResponse(data=UserData(user=user, address=address))


@app.post("/users/", response_model=DataResponse.single_by_key("user", User))
def create_user_(user: User):
    return DataResponse(data={"user": user})


@app.get(
        "/users/",
        response_model=ListResponse[User],
        responses=responses_for_codes(400, 500),
)
def get_user_list_(
    pagination: PaginationParamsQuery,
    sort: SortParams = Depends(get_sort_params("name", "age")),
):
    print(pagination)
    print(sort)
    users = [User(name="Name", age=20), User(name="Name 2", age=22)]
    total_count = 12

    # Response generation
    return ListResponse[User].from_list(
        users, total_count, pagination, "Custom response message"
    )


router = APIRouter(prefix="/errors", tags=["Error"])


@router.get(
        "/request-with-http-error/",
        response_model=DataResponse.single_by_key("user", User),
)
def get_with_http_error_():
    raise HTTPException(
        status_code=http.HTTPStatus.NOT_FOUND,
        detail="User with ID 12 isn't found",
    )


@router.post(
        "/request-with-uncaught-error/",
        response_model=DataResponse.single_by_key("user", User),
)
def create_user_with_error_(user: User):
    raise Exception("Some error")


app.include_router(router)
