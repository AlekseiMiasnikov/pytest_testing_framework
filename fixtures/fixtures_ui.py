import pytest

from pages import GooglePage


@pytest.fixture(scope='function')
def google_page(browser):
    return GooglePage(browser)
