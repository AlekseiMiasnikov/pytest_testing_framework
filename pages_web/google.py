from core.utils.allure_wrapper import step
from core.utils.selene import have
from elements.el import Elements


class Google(Elements):
    def __init__(self, browser):
        self.browser = browser

    @step('Открытие страницы браузера')
    def open(self, url='/'):
        self.browser.open(url)

    @step('Заполнения поля значением {value}')
    def fill_search(self, value):
        self.el('[title="Поиск"]').set_value(value)

    @step('Клик по кнопке "Поиск"')
    def click_button_search(self):
        self.el('[title="Поиск"]').press_enter()

    @step('Клик по кнопке {name}')
    def click_button_calculator(self, name):
        self.el(f'//div[text() = "{name}"]').press_enter()

    @step('Проверка наличия на странице "{expression}" и "expression_result"')
    def check_expression_calculator(self, expression, expression_result):
        self.el('//span[@class="vUGUtc"]').should(have.text(expression))
        self.el('//span[@class="qv3Wpe"]').should(have.text(expression_result))
