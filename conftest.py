import os
import re
import shutil
from math import ceil

import pytest
from os import getenv
from glob import glob
from os.path import join
from pathlib import Path
from selenium import webdriver
from testrail_api import TestRailAPI
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from webdriver_manager.chrome import ChromeDriverManager
from selene.support.shared import config, browser as driver

from core.utils.testrail import TestRail
from core.utils.helpers import get_settings, get_count_tests, get_fixtures, formatted_time_for_testrail, \
    copy_files

mode = 'local'
settings_config = {}
testrail = TestRail()
testrail_test_run = 0
testrail_api = TestRailAPI(
    url=getenv('TESTRAIL_URL'),
    email=getenv('TESTRAIL_EMAIL'),
    password=getenv('TESTRAIL_PASSWORD'),
    verify=False
) if int(getenv('TESTRAIL_ENABLED')) == 1 else None
temp_files = join(Path(__file__).parent, getenv("ALLURE_DIR"))

pytest_plugins = get_fixtures()


def pytest_sessionstart():
    disable_warnings(InsecureRequestWarning)
    global settings_config, testrail_api, testrail_test_run
    settings_config = get_settings(environment=getenv('environment'))
    if int(getenv('TESTRAIL_ENABLED')) == 1 and int(getenv("ALLURE_FOR_TESTRAIL_ENABLED")) == 0:
        testrail_test_run = testrail.create_test_run(tr=testrail_api)
    if not os.path.exists(temp_files):
        os.mkdir(temp_files)


def pytest_sessionfinish(session):
    reporter = session.config.pluginmanager.get_plugin('terminalreporter')
    is_full_tests_collections = session.testscollected == get_count_tests(reporter)
    if is_full_tests_collections and int(getenv('TESTRAIL_ENABLED')) == 1:
        if int(getenv('ALLURE_FOR_TESTRAIL_ENABLED')) == 1:
            testrail.set_statuses(tr=testrail_api, data={'test_run_id': testrail_test_run})
            copy_files(source_folder=temp_files, destination_folder=join(Path(__file__).parent, 'reports'))
            shutil.rmtree(temp_files, ignore_errors=True)
        if int(getenv('TESTRAIL_AUTOCLOSE_TESTRUN')) == 1 and testrail_test_run:
            testrail.close_test_run(tr=testrail_api, run_id=testrail_test_run)
    for file in glob(f'{temp_files}/*'):
        filename = file.split('\\')[-1]
        ext = filename.split('.')[-1]
        filename_without_ext = filename.split('.')[0]
        if re.match(r'^-?[0-9]+$', filename_without_ext) and ext == 'png':
            os.remove(file)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    with open(f'{temp_files}/mode.txt', 'w') as file:
        file.write(mode)
    result = yield
    report = result.get_result()
    if int(getenv('TESTRAIL_ENABLED')) == 0 or int(getenv("ALLURE_FOR_TESTRAIL_ENABLED")) == 1 or call.when != 'call' \
            or not item.get_closest_marker('testrail_ids'):
        return
    testrail_ids = item.get_closest_marker('testrail_ids').kwargs.get('ids')
    status = 5
    screenshot = None
    if report.outcome == 'passed':
        status = 1
    for case_id in testrail_ids:
        if item.funcargs.get('browser') is not None:
            screenshot = item.funcargs['browser'].last_screenshot
        testrail.set_status(
            tr=testrail_api,
            data={
                'case_id': case_id,
                'status': status,
                'test_run_id': testrail_test_run,
                'screenshot': screenshot,
                'elapsed': formatted_time_for_testrail(ceil(call.duration)),
                'comment': f'Tests is running to {mode}'
            }
        )


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
    config.reports_folder = temp_files
    config.window_width = settings_config['BROWSER_WINDOW_WIDTH']
    config.window_height = settings_config['BROWSER_WINDOW_HEIGHT']
    config.timeout = settings_config['TIMEOUT']
    config.base_url = settings_config['APPLICATION_URL']
    yield driver
    driver.quit()
