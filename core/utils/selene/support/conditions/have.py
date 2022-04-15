import warnings
from typing import Any

from core.utils.selene.core import match
from core.utils.selene.core.condition import Condition
from core.utils.selene.core.entity import Element, Collection, Browser
from core.utils.selene.support.conditions import not_ as _not_

no = _not_


def exact_text(value) -> Condition[[], Element]:
    return match.element_has_exact_text(value)


def text(partial_value) -> Condition[[], Element]:
    return match.element_has_text(partial_value)


def js_property(name: str, value: str = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.js_property(foo).value(bar) instead',
            DeprecationWarning,
        )
        return match.element_has_js_property(name).value(value)

    return match.element_has_js_property(name)


def css_property(name: str, value: str = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.css_property(foo).value(bar) instead',
            DeprecationWarning,
        )
        return match.element_has_css_property(name).value(value)

    return match.element_has_css_property(name)


def attribute(name: str, value: str = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.attribute(foo).value(bar) instead',
            DeprecationWarning,
        )
        return match.element_has_attribute(name).value(value)

    return match.element_has_attribute(name)


def value(text) -> Condition[[], Element]:
    return match.element_has_value(text)


def value_containing(partial_text) -> Condition[[], Element]:
    return match.element_has_value_containing(partial_text)


def css_class(name) -> Condition[[], Element]:
    return match.element_has_css_class(name)


def tag(name: str) -> Condition[[], Element]:
    return match.element_has_tag(name)


def tag_containing(name: str) -> Condition[[], Element]:
    return match.element_has_tag_containing(name)


def size(number: int) -> Condition[[], Collection]:
    return match.collection_has_size(number)


def size_less_than(number: int) -> Condition[[], Collection]:
    return match.collection_has_size_less_than(number)


def size_less_than_or_equal(number: int) -> Condition[[], Collection]:
    return match.collection_has_size_less_than_or_equal(number)


def size_greater_than(number: int) -> Condition[[], Collection]:
    return match.collection_has_size_greater_than(number)


def size_at_least(number: int) -> Condition[[], Collection]:
    warnings.warn(
        'might be deprecated; use have.size_greater_than_or_equal instead',
        PendingDeprecationWarning,
    )
    return match.collection_has_size_greater_than_or_equal(number)


def size_greater_than_or_equal(number: int) -> Condition[[], Collection]:
    return match.collection_has_size_greater_than_or_equal(number)


def texts(*partial_values: str) -> Condition[[], Collection]:
    return match.collection_has_texts(*partial_values)


def exact_texts(*values: str) -> Condition[[], Collection]:
    return match.collection_has_exact_texts(*values)


def url(exact_value: str) -> Condition[[], Browser]:
    return match.browser_has_url(exact_value)


def url_containing(partial_value: str) -> Condition[[], Browser]:
    return match.browser_has_url_containing(partial_value)


def title(exact_value: str) -> Condition[[], Browser]:
    return match.browser_has_title(exact_value)


def title_containing(partial_value: str) -> Condition[[], Browser]:
    return match.browser_has_title_containing(partial_value)


def tabs_number(value: int) -> Condition[[], Browser]:
    return match.browser_has_tabs_number(value)


def tabs_number_less_than(value: int) -> Condition[[], Browser]:
    return match.browser_has_tabs_number_less_than(value)


def tabs_number_less_than_or_equal(value: int) -> Condition[[], Browser]:
    return match.browser_has_tabs_number_less_than_or_equal(value)


def tabs_number_greater_than(value: int) -> Condition[[], Browser]:
    return match.browser_has_tabs_number_greater_than(value)


def tabs_number_greater_than_or_equal(value: int) -> Condition[[], Browser]:
    return match.browser_has_tabs_number_greater_than_or_equal(value)


def js_returned_true(script_to_return_bool: str) -> Condition[[], Browser]:
    warnings.warn(
        'might be deprecated; use have.js_returned(True, ...) instead',
        PendingDeprecationWarning,
    )
    return match.browser_has_js_returned(True, script_to_return_bool)


def js_returned(expected: Any, script: str, *args) -> Condition[[], Browser]:
    return match.browser_has_js_returned(expected, script, *args)
