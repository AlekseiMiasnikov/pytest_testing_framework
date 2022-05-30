from core.utils.allure_wrapper import step
from elements.elements import Elements


class GooglePage(Elements):
    def __init__(self, browser):
        self.browser = browser

    @step('Открытие страницы')
    def open(self, url='/'):
        self.browser.open(url)

    @step('Заполнения поля поиска значением {value}')
    def fill_search_form(self, value):
        self.input('[title="Поиск"]').set_value(value)

    @step('Клик по кнопке поиска')
    def click_button(self):
        self.input('[title="Поиск"]').press_enter()
