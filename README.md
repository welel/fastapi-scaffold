# fastapi-scaffold

Эта библиотека для FastAPI обеспечивает структурированный подход к построению согласованных, масштабируемых и поддерживаемых HTTP API. Она обеспечивает соблюдение лучших практик для именования, операций с ресурсами и структурирования ответов со встроенными помощниками для разбиения на страницы, сортировки и обработки ошибок. Библиотека поддерживает понятные, единообразные модели ответов, упрощая документацию API и повышая общую эффективность разработки.

---
# Проектирование HTTP API

## Критерии качества API

- **Структурная целостность** — API не должно быть в виде набора несвязных точек, точки должны ложиться в общую картину.
- **Консистентность** — различные части системы сделаны похожим образом: если человек понял один кусок системы, то он должен без проблем понять и другой.
- **Очевидность/читаемость** — по названию API точек понятно что это API делает и зачем оно нужно.
- **Устойчивость к изменениям** — любой код жив до тех пор, пока в нём можно что-то менять, если в код стало сложно вносить изменения, значит его скорее всего выкинут или перепишут с нуля. Идеальное API можно бесконечно менять и от этого оно не должно становится сильно хуже.
- **Слабая связность разных сущностей** — например, есть сущности заказ и корзина; если хотим переписать корзину, то сущность заказа не должна меняться.

## Именование точек и полей

- Используйте **snake_case** для наименования параметров и полей.
- Используйте **kebab-case** для наименования эндпоинтов.
- Из записи **METHOD + URL** должно быть понятно, что делает операция.
- Не используйте одиночные слова без семантики (apply, cancel, и т.д.)
- Не используйте сокращения (за исключением устоявшихся).
- Используйте парные сущности консистентно (~~start + end~~, start + stop).
- Используйте is_, has_ префиксы для булевых переменных (is_product, has_discount).
- Избегайте двойных отрицаний (~~do_not_disturb~~, disturbing_is_allowed).
- Все API точки должны заканчиваться без символа “/”.

### Коллекции и одиночные ресурсы

Ресурс может быть **одиночным** или **коллекцией**.

Например, “`articles`” это **коллекция, потому что можем выводить списки, брать по id**, а “`balance`” пользователя одиночный объект, потому что у пользователя только 1 баланс, он не может выводить список или запрашивать балансы по id. 

Коллекции в нейминге во множественном числе “`/articles`”. Отдельный объект коллекции — это одиночный объект  “`/articles/{article_id}`”.

```
/articles     # коллекция
/articles/12  # одиночный объект коллекции
/balance      # одиночный объект
```

Коллекции могут включать вложенные коллекции. Вложенные коллекции можно создавать отдельно или вкладывать в существующую коллекцию в архитектуре API.

```
/items           # коллекция
/items/10/prices # вложенная коллекция
/prices          # или можно отдельно
```

### Операции над ресурсом

**HTTP метод определяет какую операцию мы совершаем над ресурсом**.

**Пример CRUD нейминга**:

| HTTP метод | Название точки               | Описание действия                              |
| ---------- | ---------------------------- | ---------------------------------------------- |
| **GET**    | `/api/articles`              | Получение списка статей.                       |
| **POST**   | `/api/articles`              | Создание новой статьи.                         |
| **GET**    | `/api/articles/{article_id}` | Получение конкретной статьи по ID.             |
| **PUT**    | `/api/articles/{article_id}` | Полное обновление статьи (все поля из модели). |
| **PATCH**  | `/api/articles/{article_id}` | Частичное обновление статьи.                   |
| **DELETE** | `/api/articles/{article_id}` | Удаление статьи.                               |

## GET параметры

Для GET параметров пагинации и сортировки существуют helpers, которые следует использовать. Они помогают в одном стиле задавать GET параметры во точках и упрощают работу.

### Пагинация

Параметры пагинации передаются через GET параметры:

- **page** - номер страницы (по умолчанию `1`).
- **per_page** - количество элементов на странице (по умолчанию `10`).

**Пример использования PaginationParamsQuery:**

```python
from fastapi_scaffold import PaginationParamsQuery

@app.get('/articles')
async def get_articles(
    # Задаст параметры page, per_page
    pagination: PaginationParamsQuery,
):
    print(pagination.page) # 1
    print(pagination.per_page) # 10
```

### Сортировка

Параметры сортировки передаются через GET параметры:

- **sort_by** - поле, по которому осуществляется сортировка (по умолчанию 1 доступный элемент).
- **sort_order** - направление сортировки (`asc` для возрастания, `desc` для убывания, по умолчанию `desc`).

**Пример использования get_sort_params:**

```python
from fastapi_scaffold import get_sort_params, SortParams

@app.get('/articles')
async def get_articles(
    # Задаст параметры sort_by, sort_order
    sort: SortParams = Depends(get_sort_params("name", "created_at")),
):
    print(sort.sort_by) # created_at
    print(sort.sort_order) # desc
```

## Структура ответов

Общая, единая структура ответов от API поддерживает консистентность и читаемость. Далее приводится описание структуры и логики ответов.

- На создание/обновление/удаление возвращаем ресурс над которым было совершено действие.

### Базовый ответ

Все ответы от API имеют 2 обязательных поля — флаг успешности запроса (success) и сообщение (message).
```python
{
    "success": True,
    "message": "Any success message"
}
```

### Ответ с данными

Данные бизнес логики (не сервисные) всегда помещаем в поле **data**. Когда помещаем данные в **data**, всегда делаем вложение, т.е. в data не надо помещать сразу поля конкретного ресурса, создаём ключ с названием ресурса и помещаем туда. Такой подход позволяет поддерживать устойчивость к изменениям. В будущем будет возможность легко расширить набор данных. 

**Пример ответа с данными:**

```python
{
    "success": True,
    "message": "Article retrieved",
    "data": {
        "article": { # Всегда делаем вложение под объект
            "id": 1,
            "title": "Some title"
        }
    }
}

```

### Ответ с пагинацией

Данные по которым двигаемся (список) помещаем всегда в одно место: **data -> list**. Если в ответе пагинация не предусматривается, то лучше помещать данные в **data** по ключу (название коллекции). Данные по пагинации помещаются в **pagination** поле на верхнем уровне. Схемы ответов обеспечивают автоматическую калькуляцию и добавку pagination данных в ответы, будет продемонстрировано далее.

**Пример ответа с данными и пагинацией:**

```python
{
    "success": True,
    "message": "Articles retrieved",
    "data": {
        "list": [ # Пагинация всегда идёт по данным из list
            {
                "id": 1,
                "title": "Some title"
            },
            {
                "id": 2,
                "title": "Some title 2"
            }
        ]
    },
    "pagination": {
        "total_items": 10,
        "page": 1,
        "items_per_page": 3,
        "next_page": 2,
        "prev_page": null,
        "total_pages": 4
    }
}
```

## Классы ответов

Структура ответов в FastAPI приложении задаётся через pydantic модели (схемы). Базовые схемы ответов используют [дженерики](https://docs.python.org/3/library/typing.html#generics) для унификации создания конечных схем. Использование базовых схем позволяет без труда следовать структуре ответов описанной выше. 

### Базовые ответы

#### Пример использования BaseResponse

```python
from fastapi_scaffold import BaseResponse

@app.get('/ping', response_model=BaseResponse)
async def ping():
	return BaseResponse(message="Pong")
	# success = True, message = "Pong"
```

#### Пример использования HTTP response

Для каждого HTTP статуса существует своя схема, где установлены success и message в соответствии с HTTP статусом. В данной библиотеке ошибочные ответы возвращаются через `raise HTTPException`, это будет рассмотрено далее.

```python
from fastapi_scaffold import Response200

@app.get('/ping', response_model=Response200)
async def ping():
	return Response200() # success = True, message = "OK"
```

#### Пример использования responses_for_codes

Для добавления в swagger документацию ответов с различными HTTP статусами можно использовать responses_for_codes. Эта функция задаст базовые ответы с success и message в соответствии с HTTP статусом.

```python
from fastapi_scaffold import Response200

@app.get(
    '/ping',
    response_model=Response200,
    responses=responses_for_codes(401, 402, 500),
)
async def ping(...):
    return Response200()
```

### Ответ с данными

#### Пример использования DataResponse

```python
from fastapi_scaffold import Schema, DataResponse

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
	'/users/{user_id}',
	# Сгенерирует схему с data = UserData
	response_model=DataResponse[UsersData],
)
async def get_user(...):
    user = User(name=f"Name", age=22)
    address = Address(country="Russia", city="Sochi")
	  return DataResponse(data=UserData(user=user, address=address))
```

Swagger схема и ответ будут следующей структуры:

```python
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "user": {
      "name": "Name",
      "age": 22
    },
    "address": {
      "country": "Russia",
      "city": "Sochi"
    }
  }
}
```

#### Пример использования DataResponse.single_by_key

В подавляющем большинстве случаев необходимо вернуть один ресурс по конкретному ключу. Для генерации `response_model` можно использовать `single_by_key`.

```python
from fastapi_scaffold import Schema, DataResponse

@app.get(
	'/users/{user_id}',
	# Сгенерирует схему с data = {"user": <user>}
	response_model=DataResponse.single_by_key("user", User),
)
async def get_user():
    user = User(name="Name", age=22)
	  return DataResponse(data={"user": user})
```

Swagger схема и ответ будут следующей структуры:

```python
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "user": {
      "name": "Name",
      "age": 22
    }
  }
}
```

### Ответ с пагинацией

#### Пример использования ListResponse и from_list

```python
from fastapi_scaffold import ListResponse, PaginationParamsQuery

@app.get(
	'/users',
	# Сгенерирует схему:
	# data: {"list": [<user>, ...]}, "pagination": {<pagination>}, ...
	response_model=ListResponse[User],
)
async def get_users(
		pagination: PaginationParamsQuery,	
):
    users = [User(name="Name", age=20), User(name="Name 2", age=22)]
    total_count = 12

    # Генерирует ответ по схеме и добавляет данные пагинации
    return ListResponse[User].from_list(
        users, total_count, pagination
    )

```

Swagger схема и ответ будут следующей структуры:

```python
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "list": [
      {
        "name": "Name",
        "age": 20
      },
      {
        "name": "Name 2",
        "age": 22
      }
    ]
  },
  "pagination": {
    "total_items": 12,
    "page": 1,
    "items_per_page": 2,
    "next_page": 2,
    "prev_page": null,
    "total_pages": 6
  }
}
```

### Ответ с ошибкой

Для полноценной работы обработчиков ответов с ошибкой необходимо инициализировать обработчики и responses приложения.

```python
from fastapi_scaffold import init_exc_handlers, init_responses

app = FastAPI()

init_responses(app)  # Установит базовые 422, 500
init_exc_handlers(app)  # Инициализирует обработчики
```

#### HTTP ошибки

`ScaffoldException` это расширение класса `starlette.exceptions.HTTPException` с изменённым интерфейсом. Ошибочные ответы возвращаются автоматически при возникновении `ScaffoldException`/`HTTPException`. Существуют отдельные классы для часто используемых ошибок.

```python
import http

from fastapi_scaffold.exc import ScaffoldException, InternalServerError

@app.get(
	'/users/{user_id}',
	response_model=DataResponse.single_by_key("user", User),
	responses=responses_for_codes(400, 404, 500),
)
async def get_user(user_id: int):

    raise ScaffoldException(
	    f"User with ID {user_id} isn't found",
	    status_code=http.HTTPStatus.NOT_FOUND,
    )

    # Пример часто используемой ошибоки.
    raise InternalServerError()
```

Swagger схема и ответ будут следующей структуры:

```python
{
  "success": False,
  "message": "User with ID 12 isn't found"
}
```

#### Ошибки валидации

FastAPI завязан на pydantic, поэтому ошибки валидации рекомендуется формировать в [стиле pydantic](https://docs.pydantic.dev/latest/errors/errors/).

К ошибкам валидации относятся:
  - ошибки валидации схем pydantic (возникают автоматически);
  - ошибки в query параметрах;
  - логические ошибки в данных.

Пример логической ошибки в данных: передали объект на создание с некоторым foreign key на другой объект, которого не существует в БД.

**Pydantic error:**

- **type**: [Тип ошибки](https://docs.pydantic.dev/latest/errors/validation_errors/). Может быть кастомный. В основном используется `"value_error"`, он подходит под большинство случаев.
- **loc**: Путь до поля с ошибкой. В теле запроса начинается с `"body"`, в query параметрах с `"query"`. Пример: `{"user": {"name": "John"}}`, если ошибка в поле *name*, то `loc = ("body", "user", "name")`.
- **msg**: Человекочитаемое сообщение об ошибке. Может быть в виде f-строки, тогда параметры необходимо передать в **ctx**.
- **input**: Значение в котором ошибка.
- **ctx**: Контекст для форматирования **msg**.

##### Формирование ошибок валидации

**Порядок валидации данных:**

  1. Написание схем с валидацией типов и ограничений `Field`.
  2. Добавление валидации через декоратор `@validate`.
  3. Возбуждение `fastapi_scaffold.exc.ValidationError`.

Как пользоваться первыми двумя шагами описано в [документации pydantic](https://docs.pydantic.dev/latest/). Рассмотрим примеры возбуждения ошибки валидации данной библиотеки.

```python
from fastapi_scaffold.exc import ErrorDetails, ValidationError

class Service(Schema):
    id: int
    host: str

class CreateUser(Schema):
    name: str = Field(..., examples=["John"])
    service: Service

@app.post(
        "/users",
        response_model=DataResponse.single_by_key("user", CreateUser),
)
def create_user_with_service(
    user: CreateUser,
    start: int = Query(0),
    end: int = Query(0),
    app: str = Query("default"),
):

    # ValidationError принимает список ErrorDetails.

    # Полноценный пример исключения.
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

    # Короткая форма исключения.
    if user.service.id == 1:
        raise ValidationError([
            ErrorDetails(
                type="value_error",
                loc=("body", "user", "service", "id"),
                msg=f"Service with ID {user.service.id} doesn't exist",
                input=user.service.id,
            )
        ])

    # Ещё короче, без f-строки, потому что ID можно увидеть в input.
    # Такое можно использовать, если ошибка предназначается
    # разработчику, а не пользователю.
    if user.service.id == 2:
        raise ValidationError([
            ErrorDetails(
                type="value_error",
                loc=("body", "user", "service", "id"),
                msg="Service with this ID doesn't exist",
                input=user.service.id,
            )
        ])

    # Ошибка валидации query параметра.
    if app != "default":
        raise ValidationError([
            ErrorDetails(
                type="value_error",
                loc=("query", "app"),
                msg="App doesn't exist (accepts only 'default')",
                input=app,
            )
        ])

    # Обобщённая ошибка, когда задействовано несколько полей.
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
```

Swagger схема ошибок валидации:

```python
{
  "success": false,
  "message": "Validation error",
  "errors": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "user",
        "service",
        "id"
      ],
      "msg": "Service with ID 0 doesn't exist",
      "input": 0,
      "ctx": {
        "service_id": 0
      }
    }
  ]
}
```

#### Неотловленные ошибки

При возникновении исключения, которое не было отловлено в реализации точки, вернётся `Response500`. Если при инициализации обработчиков был передан флаг debug = True, тогда к базовому ответу будет добавлен traceback, а к message сообщение об ошибке.


## Работа с запросом

### Пагинация

**Пример использования paginate:**

Функция возвращает кортеж из двух элементов: список запрошенных объектов и общее количество объектов до применения пагинации.

```python
from fastapi_scaffold import PaginationParamsQuery, paginate

@app.get('/articles')
async def get_articles(
    pagination: PaginationParamsQuery,
    session: AsyncSession = Depends(get_session()),
):
    stmt = select(Article).where(Article.is_original.is_(True))
    articles, count = paginate(session, stmt, pagination=pagination)
```

### Сортировка

**Пример использования sort:**

```python
from fastapi_scaffold import get_sort_params, SortParams, sort

@app.get('/articles')
async def get_articles(
    sorting: SortParams = Depends(get_sort_params("title", "created_at")),
    session: AsyncSession = Depends(get_session()),
):
    stmt = select(Article).where(Article.is_original.is_(True))
    stmt = sort(stmt, sorting=sorting)
```
