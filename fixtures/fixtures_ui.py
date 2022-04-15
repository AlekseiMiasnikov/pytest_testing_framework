import pytest

from helpers.utils import mobile_config
from pages import GooglePage
from screens.main_screen import MainScreen


@pytest.fixture(scope='function')
def google_page(browser):
    return GooglePage(browser)


@pytest.fixture(scope='function')
def main_screen_geekbench(mobile_application):
    return MainScreen(mobile_application(mobile_configuration=mobile_config(app='geekbench')))


@pytest.fixture(scope='function')
def main_screen_notepad(mobile_application):
    return MainScreen(mobile_application(mobile_configuration=mobile_config(app='notepad')))
