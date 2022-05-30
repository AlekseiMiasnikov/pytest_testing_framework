import pytest
from pages_web import Google


@pytest.fixture(scope='function')
def google(browser):
    return Google(browser)
