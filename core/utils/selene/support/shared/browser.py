import os
import warnings
from typing import Union, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from core.utils.selene.common.helpers import is_absolute_url
from core.utils.selene.common.none_object import _NoneObject
from core.utils.selene.core.configuration import Config
from core.utils.selene.core.entity import Browser, Collection
from core.utils.selene.support.shared.config import SharedConfig
from core.utils.selene.support.webdriver import WebHelper


class SharedBrowser(Browser):
    def __init__(self, config: SharedConfig):
        self._latest_screenshot = _NoneObject(
            'selene.SharedBrowser._latest_screenshot'
        )
        self._latest_page_source = _NoneObject(
            'selene.SharedBrowser._latest_page_source'
        )
        super().__init__(config)

    @property
    def config(self) -> SharedConfig:
        return self._config

    def with_(self, config: Config = None, **config_as_kwargs) -> Browser:
        return SharedBrowser(self.config.with_(config, **config_as_kwargs))

    def open(self, relative_or_absolute_url: str):
        width = self.config.window_width
        height = self.config.window_height

        if width and height:
            self.driver.set_window_size(int(width), int(height))

        is_absolute = is_absolute_url(relative_or_absolute_url)
        base_url = self.config.base_url
        url = (
            relative_or_absolute_url
            if is_absolute
            else base_url + relative_or_absolute_url
        )

        self.config.get_or_create_driver().get(url)

        return self

    @property
    def driver(self) -> WebDriver:
        webdriver: WebDriver = self.config.driver

        def return_driver(this) -> WebDriver:
            warnings.warn(
                'deprecated; use `browser.driver` over `browser.driver()`',
                DeprecationWarning,
            )
            return webdriver

        webdriver.__class__.__call__ = return_driver

        return webdriver

    def save_screenshot(self, file: str = None):

        if not file:
            file = self.config.generate_filename(suffix='.png')
        if file and not file.lower().endswith('.png'):
            file = os.path.join(file, f'{next(self.config.counter)}.png')
        folder = os.path.dirname(file)
        if not os.path.exists(folder) and folder:
            os.makedirs(folder)
        self.config.last_screenshot = WebHelper(self.driver).save_screenshot(
            file
        )

        return self.config.last_screenshot

    @property
    def last_screenshot(self) -> str:
        return self.config.last_screenshot

    @property
    def latest_screenshot(self) -> str:
        warnings.warn(
            'deprecated, use browser.last_screenshot property',
            DeprecationWarning,
        )

        class CallableString(str):
            def __new__(cls, value):
                obj = str.__new__(cls, value)
                obj._value = value
                return obj

            def __call__(self, *args, **kwargs):
                warnings.warn(
                    'browser.latest_screenshot() is deprecated, '
                    'use browser.last_screenshot as a property. ',
                    DeprecationWarning,
                )
                return self[:]

            def __bool__(self):
                return bool(self._value)

        return CallableString(self.last_screenshot)

    def save_page_source(self, file: str = None) -> Optional[str]:

        if not file:
            file = self.config.generate_filename(suffix='.html')

        saved_file = WebHelper(self.driver).save_page_source(file)

        self.config.last_page_source = saved_file

        return saved_file

    @property
    def last_page_source(self) -> str:
        return self.config.last_page_source

    @property
    def latest_page_source(self):
        warnings.warn(
            'browser.latest_page_source prop is deprecated, use browser.last_page_source',
            DeprecationWarning,
        )
        return self.config.last_page_source

    def quit(self) -> None:
        self.config.reset_driver()

    def quit_driver(self):
        warnings.warn(
            'deprecated; use browser.quit() instead', DeprecationWarning
        )
        self.quit()

    def close(self):
        warnings.warn(
            'deprecated; use browser.close_current_tab() instead',
            DeprecationWarning,
        )
        self.close_current_tab()

    def set_driver(self, webdriver: WebDriver):
        warnings.warn(
            'use config.driver = webdriver '
            'or '
            'config.set_driver = lambda: webdriver '
            'instead',
            DeprecationWarning,
        )

        self.config.driver = webdriver

    def open_url(self, absolute_or_relative_url):
        warnings.warn(
            'use browser.open instead of browser.open_url or open_url',
            DeprecationWarning,
        )
        return self.open(absolute_or_relative_url)

    def elements(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            'use browser.all instead of browser.elements or elements',
            DeprecationWarning,
        )
        return self.all(css_or_xpath_or_by)

    def wait_to(self, webdriver_condition, timeout=None, polling=None):
        warnings.warn(
            'use browser.should instead of browser.wait_to or wait_to',
            DeprecationWarning,
        )
        tuned_self = (
            self if timeout is None else self.with_(Config(timeout=timeout))
        )

        return tuned_self.should(webdriver_condition)

    def execute_script(self, script, *args):
        warnings.warn(
            'use browser.driver.execute_script instead of execute_script',
            DeprecationWarning,
        )
        return self.driver.execute_script(script, *args)

    def title(self):
        warnings.warn(
            'use browser.driver.title or browser.get(query.title) instead',
            DeprecationWarning,
        )
        return self.driver.title

    def take_screenshot(self, path=None, filename=None):
        warnings.warn(
            'deprecated; use browser.save_screenshot(filename) instead',
            DeprecationWarning,
        )
        return self.save_screenshot(
            os.path.join(path, filename)
            if path and filename
            else filename or path
        )
