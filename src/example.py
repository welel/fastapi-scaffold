import http

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import Field

from fastapi_scaffold import FastAPIScaffold
from fastapi_scaffold.exc import ErrorDetails, ValidationError
from fastapi_scaffold.http_responses import responses_for_codes
from fastapi_scaffold.pagination import PaginationParamsQuery
from fastapi_scaffold.responses import DataResponse, ListResponse, Schema
from fastapi_scaffold.sorting import SortParams, get_sort_params


DEBUG = True

app = FastAPI()

FastAPIScaffold(app, debug=DEBUG)


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


pydantic_router = APIRouter(prefix="/pyerrors", tags=["Pydantic Error"])


class Service(Schema):
    id: int
    host: str


class CreateUser(Schema):
    name: str = Field(..., examples=["John"])
    service: Service


@pydantic_router.post(
        "/users",
        response_model=DataResponse.single_by_key("user", CreateUser),
)
def create_user_with_service(
    user: CreateUser,
    start: int = Query(0),
    end: int = Query(0),
    app: str = Query("default"),
):

    # Full pydantic error
    if user.service.id == 0:
        raise ValidationError([
            ErrorDetails(
                type=ErrorDetails.Type.value_error,
                loc=("body", "user", "service", "id"),
                msg="Service with ID {service_id} doesn't exist",
                input=user.service.id,
                ctx={"service_id": user.service.id},
            )
        ])

    # Short form of pydantic error
    if user.service.id == 1:
        raise ValidationError([
            ErrorDetails(
                type="value_error",
                loc=("body", "user", "service", "id"),
                msg=f"Service with ID {user.service.id} doesn't exist",
                input=user.service.id,
            )
        ])

    # Shorter form of pydantic error
    # Without f-str cause we can see the value in the `input`
    if user.service.id == 2:
        raise ValidationError([
            ErrorDetails(
                type="value_error",
                loc=("body", "user", "service", "id"),
                msg="Service with this ID doesn't exist",
                input=user.service.id,
            )
        ])

    # Another level and type example
    if not user.name:
        raise ValidationError([
            ErrorDetails(
                type=ErrorDetails.Type.missing,
                loc=("body", "user", "name"),
                msg="Missing user name",
                input=user.name,
            )
        ])

    # Query validation
    if app != "default":
        raise ValidationError([
            ErrorDetails(
                type="value_error",
                loc=("query", "app"),
                msg="App doesn't exist (accepts only 'default')",
                input=app,
            )
        ])

    # Query validation for several params
    if start > end:
        raise ValidationError([
            ErrorDetails(
                type="value_error",
                loc=("query",),
                msg=f"Start {start} more than end {end}",
                input=(start, end),
            )
        ])

    return DataResponse(data={"user": user})


app.include_router(pydantic_router)
