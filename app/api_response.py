from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")  # 泛型类型变量

class APIResponse(GenericModel, Generic[T]):
    error_code: int
    error_message: str
    data: Optional[T] = None  # 可为任意类型，例如 User、List[User] 等


def wrap_api_response(data: T, error_code: int = 0, error_message: str = "") -> APIResponse[T]:
    return APIResponse(error_code=error_code, error_message=error_message, data=data)