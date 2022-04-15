from __future__ import annotations

import time
from typing import Generic, Callable, TypeVar, Optional

from core.utils.selene.common.fp import identity
from core.utils.selene.core.exceptions import TimeoutException

T = TypeVar('T')
R = TypeVar('R')
E = TypeVar('E')

Lambda = Callable[[T], R]
Proc = Callable[[T], None]
Predicate = Callable[[T], bool]

Fn = Callable[[T], R]


class Query(Generic[T, R]):
    def __init__(self, description: str, fn: Callable[[T], R]):
        self._description = description
        self._fn = fn

    def __call__(self, entity: T) -> R:
        return self._fn(entity)

    def __str__(self):
        return self._description


class Command(Query[T, None]):
    pass


class Wait(Generic[E]):

    def __init__(
            self,
            entity: E,
            at_most: int,
            or_fail_with: Optional[Callable[[TimeoutException], Exception]] = None,
    ):
        self._entity = entity
        self._timeout = at_most
        self._hook_failure = or_fail_with or identity

    def at_most(self, timeout: int) -> Wait[E]:
        return Wait(self._entity, timeout, self._hook_failure)

    def or_fail_with(
            self, hook_failure: Optional[Callable[[TimeoutException], Exception]]
    ) -> Wait[E]:

        return Wait(self._entity, self._timeout, hook_failure)

    @property
    def hook_failure(
            self,
    ) -> Optional[Callable[[TimeoutException], Exception]]:
        return self._hook_failure

    def for_(self, fn: Callable[[E], R]) -> R:
        finish_time = time.time() + self._timeout

        while True:
            try:
                return fn(self._entity)
            except Exception as reason:
                if time.time() > finish_time:
                    reason_message = str(reason)

                    reason_string = '{name}: {message}'.format(
                        name=reason.__class__.__name__, message=reason_message
                    )
                    timeout = self._timeout
                    entity = self._entity

                    failure = TimeoutException(
                        f'''

Timed out after {timeout}s, while waiting for:
{entity}.{fn}

Reason: {reason_string}'''
                    )

                    raise self._hook_failure(failure)

    def until(self, fn: Callable[[E], R]) -> bool:
        try:
            self.for_(fn)
            return True
        except TimeoutException:
            return False

    def command(self, description: str, fn: Callable[[E], None]) -> None:
        self.for_(Command(description, fn))

    def query(self, description: str, fn: Callable[[E], R]) -> R:
        return self.for_(Query(description, fn))
