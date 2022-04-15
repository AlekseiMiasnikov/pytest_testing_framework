from typing import Union

from core.utils.selene.core.entity import Element, Collection
from core.utils.selene.support.shared import browser


def s(css_or_xpath_or_by: Union[str, tuple]) -> Element:
    return browser.element(css_or_xpath_or_by)


def ss(css_or_xpath_or_by: Union[str, tuple]) -> Collection:
    return browser.all(css_or_xpath_or_by)
