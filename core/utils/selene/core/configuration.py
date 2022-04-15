from __future__ import annotations

from typing import Callable, Optional, Union

from selenium.webdriver.remote.webdriver import WebDriver

from core.utils.selene.common.none_object import _NoneObject
from core.utils.selene.core.exceptions import TimeoutException
from core.utils.selene.core.wait import Wait


def _strip_first_underscore(name: str) -> str:
    return name[1:] if name.startswith('_') else name


class Config:
    def __init__(
            self,
            driver: Optional[Union[WebDriver, Callable[[], WebDriver]]] = None,
            timeout: int = 4,
            hook_wait_failure: Optional[
                Callable[[TimeoutException], Exception]
            ] = None,
            base_url: str = '',
            set_value_by_js: bool = False,
            type_by_js: bool = False,
            wait_for_no_overlap_found_by_js: bool = False,
            window_width: Optional[int] = None,
            window_height: Optional[int] = None,
            log_outer_html_on_failure: bool = False,
    ):
        self._driver = driver
        self._timeout = timeout
        self._hook_wait_failure = hook_wait_failure

        self._base_url = base_url
        self._set_value_by_js = set_value_by_js

        self._type_by_js = type_by_js
        self._wait_for_no_overlap_found_by_js = wait_for_no_overlap_found_by_js
        self._window_width = window_width
        self._window_height = window_height
        self._log_outer_html_on_failure = log_outer_html_on_failure

    def as_dict(self, skip_empty=True):
        return {
            _strip_first_underscore(k): v
            for k, v in self.__dict__.items()
            if not (skip_empty and v is None) and not k.startswith('__')
        }

    def with_(self, config: Config = None, **config_as_kwargs) -> Config:
        return self.__class__(
            **{
                **self.as_dict(),
                **(config.as_dict() if config else {}),
                **config_as_kwargs,
            }
        )

    @property
    def driver(self) -> Union[WebDriver, _NoneObject]:
        return (
            self._driver
            if isinstance(self._driver, WebDriver)
            else (
                self._driver()
                if callable(self._driver)
                else _NoneObject(
                    'expected Callable[[], WebDriver] inside property config.driver'
                )
            )
        )

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def hook_wait_failure(self) -> Callable[[TimeoutException], Exception]:
        return self._hook_wait_failure

    def wait(self, entity):
        return Wait(
            entity, at_most=self.timeout, or_fail_with=self.hook_wait_failure
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def set_value_by_js(self) -> bool:
        return self._set_value_by_js

    @property
    def type_by_js(self) -> bool:
        return self._type_by_js

    @property
    def wait_for_no_overlap_found_by_js(self) -> bool:
        return self._wait_for_no_overlap_found_by_js

    @property
    def window_width(self) -> Optional[int]:
        return self._window_width

    @property
    def window_height(self) -> Optional[int]:
        return self._window_height

    @property
    def log_outer_html_on_failure(self) -> bool:
        return self._log_outer_html_on_failure
