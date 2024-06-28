from contextvars import ContextVar
from typing import Generic, Optional, TypeVar

from server.model.user import LoggingId

T = TypeVar("T")


class ContextWrapper(Generic[T]):
    def __init__(self, value: ContextVar[T]):
        self.__value = value

    def set(self, value: T):
        return self.__value.set(value)

    def get(self, default: Optional[T] = None):
        return self.__value.get(default)

    def reset(self, token):
        self.__value.reset(token)

    @property
    def value(self):
        return self.__value.get()


logging_context: ContextWrapper[LoggingId] = ContextWrapper(ContextVar("server.lib.logger.logging_ctx"))


def set_user_id(user_id: int):
    if logging_context.value:
        logging_context.value.user_id = user_id
