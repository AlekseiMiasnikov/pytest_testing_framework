from allure import title, description, suite, parent_suite

from core.utils.testrail import TestRail
from data.jsonplaceholder.response import GET_RESPONSE_JSONPLACEHOLDER
from helpers.utils import asserts


@parent_suite('[Pytest][API]')
@suite('jsonplaceholder')
class TestApiJsonPlaceHolder:
    @TestRail.suite('API: jsonplaceholder')
    @title('jsonplaceholder: Поиск')
    @description('Поиск с ресурса jsonplaceholder. GET: /posts/1')
    @TestRail.id('id_test_case')
    def test_api_jsonplaceholder_get(self, api_jsonplaceholder):
        asserts(
            actual_data=api_jsonplaceholder.jsonplaceholder_get(),
            asserts_data=GET_RESPONSE_JSONPLACEHOLDER
        )
