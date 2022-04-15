import warnings
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from core.utils.selene.common.helpers import on_error_return_false


class WebHelper:

    def __init__(self, driver: Optional[WebDriver]):
        self._driver = driver

    def is_browser_still_alive(self):
        return on_error_return_false(lambda: self._driver.title is not None)

    def save_page_source(self, file: str) -> Optional[str]:
        if not file.lower().endswith('.html'):
            warnings.warn(
                "name used for saved pagesource does not match file "
                "type. It should end with an `.html` extension",
                UserWarning,
            )

        html = self._driver.page_source

        try:
            with open(file, 'w', encoding="utf-8") as f:
                f.write(html)
        except OSError:
            return None
        finally:
            del html

        return file

    def save_screenshot(self, file: str) -> Optional[str]:
        if not file.lower().endswith('.png'):
            warnings.warn(
                "name used for saved pagesource does not match file "
                "type. It should end with an `.png` extension",
                UserWarning,
            )

        return file if self._driver.get_screenshot_as_file(file) else None
