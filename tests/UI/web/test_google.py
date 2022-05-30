from allure import title, description, suite, parent_suite


@parent_suite('Pytest - WEB - UI')
@suite('Google')
class TestGoogle:
    @title('Google - Поиск - Калькулятор')
    @description('Поиск слова "Калькулятор" с помощью "google.com" и выполнение выражения: "1 * 2 - 3 + 1"')
    def test_google_search_calculator(self, google):
        google.open()
        google.fill_search('Калькулятор')
        google.click_button_search()
        for calculator_btn in ['1', '×', '2', '−', '3', '+', '1', '=']:
            google.click_button_calculator(calculator_btn)
        google.check_expression_calculator(expression='1 × 2 - 3 + 1 =', expression_result='0', )
