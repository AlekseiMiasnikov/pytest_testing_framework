from os import getenv

import pytest
from requests import Session

from api import ApiJsonplaceholder
from core.utils.helpers import get_settings


settings_config = get_settings(environment=getenv('environment'))
api_session = None


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart():
    global api_session
    api_session = Session()


@pytest.fixture(scope='function')
def api_jsonplaceholder():
    return ApiJsonplaceholder(api_base_url=settings_config['API_URL'], session=api_session)
