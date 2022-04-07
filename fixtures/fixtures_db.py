from os import getenv

import pytest

from core.db.db import DB
from core.utils.helpers import get_settings

settings_config = {}
oracle_session = DB()
postgre_session = DB()


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart():
    global settings_config, oracle_session, postgre_session
    settings_config = get_settings(environment=getenv('environment'))
    if getenv('DB_ORACLE_USER_EXAMPLE') != '' and getenv('DB_ORACLE_PASSWORD_EXAMPLE') != '':
        oracle_session = DB().create_session(environment=settings_config, name='EXAMPLE_DB_POSTGRESQL')
    if getenv('DB_POSTGRESQL_USER_EXAMPLE') != '' and getenv('DB_ORACLE_PASSWORD_EXAMPLE') != '':
        postgre_session = DB().create_session(environment=settings_config, name='POSTGRE')


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish():
    if getenv('DB_ORACLE_USER_EXAMPLE') != '' and getenv('DB_ORACLE_PASSWORD_EXAMPLE') != '':
        oracle_session.close()
    if getenv('DB_POSTGRESQL_USER_EXAMPLE') != '' and getenv('DB_ORACLE_PASSWORD_EXAMPLE') != '':
        postgre_session.close()
