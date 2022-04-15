import warnings
from typing import Union

from core.utils.selene.core.entity import Element, Collection
from core.utils.selene.support.shared import browser


def s(css_or_xpath_or_by: Union[str, tuple]) -> Element:
    warnings.warn(
        'selene.support.jquery_style_selectors.s is deprecated; '
        'use selene.support.shared.jquery_style.s instead',
        DeprecationWarning,
    )
    return browser.element(css_or_xpath_or_by)


def ss(css_or_xpath_or_by: Union[str, tuple]) -> Collection:
    warnings.warn(
        'selene.support.jquery_style_selectors.ss is deprecated; '
        'use selene.support.shared.jquery_style.ss instead',
        DeprecationWarning,
    )
    return browser.all(css_or_xpath_or_by)
