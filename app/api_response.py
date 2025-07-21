import functools
from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel


T = TypeVar("T")  # 泛型类型变量

class APIResponse(GenericModel, Generic[T]):
    error_code: int
    error_message: str
    data: Optional[T] = None  # 可为任意类型，例如 User、List[User] 等


class APIBusinessException(Exception):
    def __init__(self, error_code: int, error_message: str):
        super().__init__(error_message)
        self.error_code = error_code
        self.error_message = error_message


def wrap_api_response(data: T, error_code: int = 0, error_message: str = "") -> APIResponse[T]:
    return APIResponse(error_code=error_code, error_message=error_message, data=data)


def handle_return_or_raise(function):
    @functools.wraps(function)
    async def wrapper(*args, **kwargs):
        try:
            return_data = await function(*args, **kwargs)
        except APIBusinessException as e:
            return APIResponse(error_code=e.error_code, error_message=e.error_message)
        print(return_data, '*'*20)
        return APIResponse(error_code=0, error_message="", data=return_data)
    return wrapper
