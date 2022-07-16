import os
import re
import shutil
from glob import glob
from math import ceil
from os import getenv
from os.path import join
from pathlib import Path

import pytest
from selenium import webdriver
from testrail_api import TestRailAPI
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from webdriver_manager.chrome import ChromeDriverManager

from core.utils.helpers import get_settings, get_count_tests, get_fixtures, formatted_time_for_testrail, \
    copy_files
from core.utils.selene.support.shared import config, browser as driver
from core.utils.testrail import TestRail

mode = 'local'
settings_config = {}
teamcity_launches = '1'
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


def pytest_sessionstart(session):
    global settings_config, testrail_api, testrail_test_run, teamcity_launches
    marks = session.config.invocation_params.args
    os.makedirs(temp_files, exist_ok=True)
    if '--teamcity_launches' in marks:
        path = f'{temp_files}/teamcity_launches.txt'
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except BaseException:
                pass
        with open(path, 'w', encoding='utf-8') as file:
            teamcity_launches = marks[marks.index('--teamcity_launches') + 1]
            file.write(teamcity_launches)
    disable_warnings(InsecureRequestWarning)
    settings_config = get_settings(environment=getenv('environment'))
    if int(getenv('TESTRAIL_ENABLED')) == 1 and int(getenv("ALLURE_FOR_TESTRAIL_ENABLED")) == 0 \
            and teamcity_launches == getenv('TEAMCITY_LAUNCHES'):
        testrail_test_run = testrail.create_test_run(tr=testrail_api)
    if not os.path.exists(temp_files):
        os.mkdir(temp_files)


def pytest_sessionfinish(session):
    reporter = session.config.pluginmanager.get_plugin('terminalreporter')
    is_full_tests_collections = session.testscollected == get_count_tests(reporter)
    if is_full_tests_collections and int(getenv('TESTRAIL_ENABLED')) == 1 \
            and teamcity_launches == getenv('TEAMCITY_LAUNCHES'):
        if int(getenv('ALLURE_FOR_TESTRAIL_ENABLED')) == 1:
            testrail.set_statuses(
                tr=testrail_api,
                data={
                    'test_run_id': testrail_test_run,
                    'teamcity_launches': teamcity_launches,
                    'run_mode': mode
                }
            )
            try:
                copy_files(source_folder=temp_files, destination_folder=join(Path(__file__).parent, 'reports'))
            except BaseException:
                pass
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
    parser.addoption('--teamcity_launches', action='store', default='1')


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


@pytest.fixture(scope='function')
def mobile_application():
    def wrapper(mobile_configuration):
        mobile_driver = webdriver.Remote(
            command_executor=settings_config['APPIUM']['HUB'],
            desired_capabilities=mobile_configuration
        )
        mobile_driver.implicitly_wait(settings_config['TIMEOUT'])
        return mobile_driver
    return wrapper
