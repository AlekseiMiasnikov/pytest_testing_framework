import pytest

from web_pages import Google


@pytest.fixture(scope='function')
def google(browser):
    return Google(browser)
