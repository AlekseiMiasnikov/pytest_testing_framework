from allure import title, description, suite, parent_suite

from core.utils.testrail import TestRail


@parent_suite('[Pytest][WEB][UI]')
@suite('Google')
class TestGoogle:
    @TestRail.suite('UI: Google')
    @title('Поиск в Google')
    @description('Открытие, ввод текста и поиск через Google')
    @TestRail.id('id_test_case')
    def test_google_search(self, google_page):
        google_page.open()
        google_page.fill_search_form('Pytest')
        google_page.click_button()
