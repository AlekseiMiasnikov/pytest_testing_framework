from __future__ import annotations

from typing import List, TypeVar, Callable

from core.utils.selene.core.exceptions import ConditionNotMatchedError
from core.utils.selene.core.wait import Predicate, Lambda

E = TypeVar('E')
R = TypeVar('R')


class Condition(Callable[[E], None]):
    @classmethod
    def by_and(cls, *conditions):
        def fn(entity):
            for condition in conditions:
                condition.call(entity)

        return cls(' and '.join(map(str, conditions)), fn)

    @classmethod
    def by_or(cls, *conditions):
        def fn(entity):
            errors: List[Exception] = []
            for condition in conditions:
                try:
                    condition.call(entity)
                    return
                except Exception as e:
                    errors.append(e)
            raise AssertionError('; '.join(map(str, errors)))

        return cls(' or '.join(map(str, conditions)), fn)

    @classmethod
    def as_not(
            cls, condition: Condition[E], description: str = None
    ) -> Condition[E]:
        condition_words = str(condition).split(' ')
        is_or_have = condition_words[0]
        name = ' '.join(condition_words[1:])
        no_or_not = 'not' if is_or_have == 'is' else 'no'
        new_description = description or f'{is_or_have} {no_or_not} {name}'

        def fn(entity):
            try:
                condition.call(entity)
            except Exception:
                return
            raise ConditionNotMatchedError()

        return cls(new_description, fn)

    @classmethod
    def raise_if_not(
            cls, description: str, predicate: Predicate[E]
    ) -> Condition[E]:
        def fn(entity: E) -> None:
            if not predicate(entity):
                raise ConditionNotMatchedError()

        return cls(description, fn)

    @classmethod
    def raise_if_not_actual(
            cls, description: str, query: Lambda[E, R], predicate: Predicate[R]
    ) -> Condition[E]:
        def fn(entity: E) -> None:
            query_to_str = str(query)
            result = (
                query.__name__
                if query_to_str.startswith('<function')
                else query_to_str
            )
            actual = query(entity)
            if not predicate(actual):
                raise AssertionError(f'actual {result}: {actual}')

        return cls(description, fn)

    def __init__(self, description: str, fn: Lambda[E, None]):
        self._description = description
        self._fn = fn

    def call(self, entity: E) -> None:
        self._fn(entity)

    @property
    def predicate(self) -> Lambda[E, bool]:
        def fn(entity):
            try:
                self.call(entity)
                return True
            except Exception as e:
                return False

        return fn

    @property
    def not_(self) -> Condition[E]:
        return self.__class__.as_not(self)

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)

    def __str__(self):
        return self._description

    def and_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_and(self, condition)

    def or_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_or(self, condition)


def not_(condition_to_be_inverted: Condition):
    return condition_to_be_inverted.not_
