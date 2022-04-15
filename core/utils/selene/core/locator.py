from typing import TypeVar, Generic, Callable

T = TypeVar('T')


class Locator(Generic[T]):
    def __init__(self, description: str, locate: Callable[[], T]):
        self._description = description
        self._locate = locate

    def __call__(self) -> T:
        return self._locate()

    def __str__(self):
        return self._description
