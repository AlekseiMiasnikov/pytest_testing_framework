from __future__ import annotations

import atexit
import itertools
import multiprocessing
import os
import time
import warnings
from typing import Optional, TypeVar, Generic, Callable, Union

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ChromeOptions, Chrome, Firefox
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType

from core.utils.selene.common.fp import pipe
from core.utils.selene.core.configuration import Config
from core.utils.selene.core.exceptions import TimeoutException
from core.utils.selene.core.wait import Wait
from core.utils.selene.support.webdriver import WebHelper

T = TypeVar('T')


class Source(Generic[T]):
    def __init__(self, value: T = None):
        self._value = value

    def put(self, value: T):
        self._value = value

    def clear(self):
        self._value = None

    @property
    def value(self) -> T:
        return self._value

    def __call__(self, *args, **kwargs):
        return self._value


class _LazyDriver:
    def __init__(self, config: SharedConfig):
        self._config = config
        self._closed: Optional[bool] = None
        self._stored: Optional[WebDriver] = None

    @property
    def _set_driver(self) -> Callable[[], WebDriver]:
        return self._config.set_driver

    @property
    def _hold_browser_open(self):
        return self._config.hold_browser_open

    def has_webdriver_started(self):
        return self._stored is not None

    def has_browser_alive(self):
        return WebHelper(self._stored).is_browser_still_alive()

    @property
    def instance(self) -> WebDriver:
        if self._closed:
            raise RuntimeError(
                'Webdriver has been closed. '
                'You need to call open(url) '
                'to open a browser again.'
            )

        if not self.has_webdriver_started():
            raise RuntimeError(
                f'No webdriver is bound to current process: '
                f'{multiprocessing.current_process().pid}. '
                f'You need to call .open(url) first.'
            )

        return self._stored

    def create(self) -> WebDriver:

        self._stored = self._set_driver()

        def quit_if_not_asked_to_hold():
            if not self._hold_browser_open:
                self.quit()

        atexit.register(quit_if_not_asked_to_hold)

        self._closed = False

        return self._stored

    def get_or_create(self) -> WebDriver:
        if self.has_browser_alive():
            return self._stored

        if self.has_webdriver_started():
            self.quit()

        return self.create()

    def quit(self):
        if self.has_webdriver_started() and not self._closed:
            try:
                self._stored.quit()
            except WebDriverException:
                pass

            self._closed = True


class SharedConfig(Config):

    def __init__(
            self,
            driver: Optional[WebDriver] = None,
            timeout: int = 4,
            base_url: str = '',
            set_value_by_js: bool = False,
            type_by_js: bool = False,
            wait_for_no_overlap_found_by_js: bool = False,
            window_width: Optional[int] = None,
            window_height: Optional[int] = None,
            hook_wait_failure: Optional[
                Callable[[TimeoutException], Exception]
            ] = None,
            log_outer_html_on_failure: bool = False,
            set_driver: Callable[[], WebDriver] = None,
            source: _LazyDriver = None,
            browser_name: str = 'chrome',
            hold_browser_open: bool = False,
            save_screenshot_on_failure: bool = True,
            save_page_source_on_failure: bool = True,
            poll_during_waits: int = 100,
            counter=None,
            reports_folder: Optional[str] = None,
            last_screenshot: Union[Optional[str], Source[str]] = None,
            last_page_source: Union[Optional[str], Source[str]] = None,
    ):

        self._browser_name = browser_name
        self._hold_browser_open = hold_browser_open
        self._source = source or _LazyDriver(self)
        self._log_outer_html_on_failure = log_outer_html_on_failure

        if driver and not set_driver:
            self._set_driver = lambda: driver
            self._source.create()
        else:
            auto_set_driver = (
                lambda: self._set_chrome_or_firefox_from_webdriver_manager()
            )
            self._set_driver = set_driver or auto_set_driver

        self._save_screenshot_on_failure = save_screenshot_on_failure
        self._save_page_source_on_failure = save_page_source_on_failure
        self._poll_during_waits = poll_during_waits
        self._counter = counter or itertools.count(
            start=int(round(time.time() * 1000))
        )
        self._reports_folder = reports_folder or os.path.join(
            os.path.expanduser('~'),
            '.selene',
            'screenshots',
            str(next(self._counter)),
        )
        self._last_screenshot = (
            last_screenshot
            if isinstance(last_screenshot, Source)
            else Source(last_screenshot)
        )
        self._last_page_source = (
            last_page_source
            if isinstance(last_page_source, Source)
            else Source(last_page_source)
        )
        super().__init__(
            driver=driver,
            timeout=timeout,
            base_url=base_url,
            set_value_by_js=set_value_by_js,
            type_by_js=type_by_js,
            wait_for_no_overlap_found_by_js=wait_for_no_overlap_found_by_js,
            window_width=window_width,
            window_height=window_height,
            hook_wait_failure=hook_wait_failure,
            log_outer_html_on_failure=log_outer_html_on_failure,
        )

    def _set_chrome_or_firefox_from_webdriver_manager(self):
        def get_chrome():
            return Chrome(
                service=ChromeService(
                    ChromeDriverManager(
                        chrome_type=ChromeType.CHROMIUM
                    ).install()
                ),
                options=ChromeOptions(),
            )

        def get_firefox():
            return Firefox(
                service=FirefoxService(GeckoDriverManager().install())
            )

        return {'chrome': get_chrome, 'firefox': get_firefox}.get(
            self.browser_name
        )()

    @property
    def driver(self) -> WebDriver:

        return self._source.instance

    def get_or_create_driver(self) -> WebDriver:
        return self._source.get_or_create()

    def quit_driver(self):
        warnings.warn(
            'shared.config.quit_driver is deprecated, '
            'use shared.config.reset_driver instead',
            DeprecationWarning,
        )
        self.reset_driver()

    def reset_driver(self):
        self.set_driver = (
            lambda: self._set_chrome_or_firefox_from_webdriver_manager()
        )

    @driver.setter
    def driver(self, value: WebDriver):
        self.set_driver = (
            lambda: value
        )
        self._source.create()

    @property
    def set_driver(self):
        return self._set_driver

    @set_driver.setter
    def set_driver(self, value: Callable[[], WebDriver]):
        self._source.quit()
        self._set_driver = value

    def generate_filename(self, prefix='', suffix=''):
        path = self.reports_folder
        next_id = next(self.counter)
        filename = f'{prefix}{next_id}{suffix}'
        file = os.path.join(path, f'{filename}')

        folder = os.path.dirname(file)
        if not os.path.exists(folder) and folder:
            os.makedirs(folder)

        return file

    def _inject_screenshot_and_page_source_pre_hooks(self, hook):
        def save_and_log_screenshot(error: TimeoutException) -> Exception:
            path = WebHelper(self.driver).save_screenshot(
                self.generate_filename(suffix='.png')
            )
            self.last_screenshot = path
            return TimeoutException(
                error.msg
                + f'''
Screenshot: file://{path}'''
            )

        def save_and_log_page_source(error: TimeoutException) -> Exception:
            filename = (
                self.last_screenshot.replace('.png', '.html')
                if self.last_screenshot
                else self.generate_filename(suffix='.html')
            )
            path = WebHelper(self.driver).save_page_source(filename)
            self.last_page_source = path
            return TimeoutException(
                error.msg
                + f'''
PageSource: file://{path}'''
            )

        return pipe(
            save_and_log_screenshot
            if self.save_screenshot_on_failure
            else None,
            save_and_log_page_source
            if self.save_page_source_on_failure
            else None,
            hook,
        )

    def wait(self, entity):
        hook = self._inject_screenshot_and_page_source_pre_hooks(
            self.hook_wait_failure
        )
        return Wait(entity, at_most=self.timeout, or_fail_with=hook)

    @Config.timeout.setter
    def timeout(self, value: int):
        self._timeout = value

    @Config.base_url.setter
    def base_url(self, value: str):
        self._base_url = value

    @Config.set_value_by_js.setter
    def set_value_by_js(self, value: bool):
        self._set_value_by_js = value

    @Config.type_by_js.setter
    def type_by_js(self, value: bool):
        self._type_by_js = value

    @Config.wait_for_no_overlap_found_by_js.setter
    def wait_for_no_overlap_found_by_js(self, value: bool):
        self._wait_for_no_overlap_found_by_js = value

    @Config.window_width.setter
    def window_width(self, value: Optional[int]):
        self._window_width = value

    @Config.window_height.setter
    def window_height(self, value: Optional[int]):
        self._window_height = value

    @Config.log_outer_html_on_failure.setter
    def log_outer_html_on_failure(self, value: bool):
        self._log_outer_html_on_failure = value

    @Config.hook_wait_failure.setter
    def hook_wait_failure(
            self, value: Callable[[TimeoutException], Exception]
    ):
        default = lambda e: e
        self._hook_wait_failure = value or default

    @property
    def last_screenshot(self) -> str:
        return self._last_screenshot.value

    @last_screenshot.setter
    def last_screenshot(self, value: str):
        self._last_screenshot.put(value)

    @property
    def last_page_source(self) -> str:
        return self._last_page_source.value

    @last_page_source.setter
    def last_page_source(self, value: str):
        self._last_page_source.put(value)

    @property
    def hold_browser_open(self) -> bool:
        return self._hold_browser_open

    @hold_browser_open.setter
    def hold_browser_open(self, value: bool):
        self._hold_browser_open = value

    @property
    def save_screenshot_on_failure(self) -> bool:
        return self._save_screenshot_on_failure

    @save_screenshot_on_failure.setter
    def save_screenshot_on_failure(self, value: bool):
        self._save_screenshot_on_failure = value

    @property
    def save_page_source_on_failure(self) -> bool:
        return self._save_page_source_on_failure

    @save_page_source_on_failure.setter
    def save_page_source_on_failure(self, value: bool):
        self._save_page_source_on_failure = value

    @property
    def browser_name(self) -> str:
        return self._browser_name

    @browser_name.setter
    def browser_name(self, value: str):
        self._browser_name = value

    @property
    def cash_elements(self) -> bool:
        warnings.warn(
            'browser.cash_elements does not work now, '
            'and probably will be renamed when implemented',
            FutureWarning,
        )
        return False

    @cash_elements.setter
    def cash_elements(self, value: bool):
        warnings.warn(
            'browser.cash_elements does not work now, '
            'and probably will be renamed when implemented',
            FutureWarning,
        )
        pass

    @property
    def start_maximized(self):
        warnings.warn(
            'browser.start_maximized does not work now, '
            'and probably will be deprecated or renamed when implemented',
            FutureWarning,
        )
        return False

    @start_maximized.setter
    def start_maximized(self, value):
        warnings.warn(
            'browser.start_maximized does not work now, '
            'and probably will be deprecated or renamed when implemented',
            FutureWarning,
        )
        pass

    @property
    def desired_capabilities(self):
        warnings.warn(
            'browser.desired_capabilities does not work now, '
            'and probably will be deprecated completely',
            FutureWarning,
        )
        return None

    @desired_capabilities.setter
    def desired_capabilities(self, value):
        warnings.warn(
            'browser.desired_capabilities does not work now, '
            'and probably will be deprecated completely',
            FutureWarning,
        )

    @property
    def poll_during_waits(self) -> int:
        warnings.warn(
            'browser.poll_during_waits might be deprecated',
            PendingDeprecationWarning,
        )
        return self._poll_during_waits or 100

    @poll_during_waits.setter
    def poll_during_waits(self, value: int):
        warnings.warn(
            'browser.poll_during_waits= might be deprecated',
            PendingDeprecationWarning,
        )
        self._poll_during_waits = value

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, value):
        self._counter = value

    @property
    def reports_folder(self) -> str:
        return self._reports_folder

    @reports_folder.setter
    def reports_folder(self, value):
        self._reports_folder = value
