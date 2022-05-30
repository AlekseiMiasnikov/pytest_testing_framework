from os import getenv

import pytest
from selenium import webdriver
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from webdriver_manager.chrome import ChromeDriverManager

from core.utils.helpers import get_settings, get_fixtures
from core.utils.selene.support.shared import config, browser as driver

mode = 'local'
settings_config = {}
pytest_plugins = get_fixtures()


def pytest_sessionstart():
    disable_warnings(InsecureRequestWarning)
    global settings_config
    settings_config = get_settings(environment=getenv('environment'))


def pytest_addoption(parser):
    parser.addoption('--mode', action='store', default='local')


@pytest.fixture(scope='function')
def browser(pytestconfig):
    global mode
    mode = pytestconfig.getoption('mode')
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_experimental_option('prefs', {
        'profile.default_content_setting_values.notifications': 1
    })
    if mode == 'selenoid':
        capabilities = {
            'browserName': settings_config['BROWSER_NAME'],
            'browserVersion': settings_config['SELENOID']['BROWSER_VERSION'],
            'selenoid:options': {
                'enableVNC': settings_config['SELENOID']['ENABLE_VNC'],
                'enableVideo': settings_config['SELENOID']['ENABLE_VIDEO']
            }
        }
        config.driver = webdriver.Remote(
            command_executor=settings_config['SELENOID']['HUB'],
            desired_capabilities=capabilities,
            options=options
        )
    else:
        config.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=options
        )
    config.browser_name = settings_config['BROWSER_NAME']
    config.window_width = settings_config['BROWSER_WINDOW_WIDTH']
    config.window_height = settings_config['BROWSER_WINDOW_HEIGHT']
    config.timeout = settings_config['TIMEOUT']
    config.base_url = settings_config['APPLICATION_URL']
    yield driver
    driver.quit()
