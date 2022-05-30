from appium.webdriver.common.appiumby import AppiumBy
from core.utils.allure_wrapper import step


class BaseScreen:
    def __init__(self, driver):
        self.driver = driver

    @step('Поиск элемента по id - {idx}')
    def find_by_id(self, idx):
        return self.driver.find_element(
            by=AppiumBy.ID,
            value=idx
        )

    @step('Поиск элемента по class - {class_name}')
    def find_by_class(self, class_name):
        return self.driver.find_element(
            by=AppiumBy.CLASS_NAME,
            value=class_name
        )

    @step('Ввод текста - "{text}"')
    def set_value(self, element, text, set_type='id'):
        if set_type == 'id':
            self.find_by_id(idx=element).send_keys(text)
        else:
            self.find_by_class(class_name=element).send_keys(text)

    @step('Клик по элементу с id - {idx}')
    def click_by_id(self, idx):
        self.find_by_id(idx=idx).click()

    @step('Клик по элементу с class - {class_name}')
    def click_by_class(self, class_name):
        self.find_by_class(class_name=class_name).click()

    @step('Получение текста у элемента с id - {idx}')
    def get_text(self, idx):
        return self.find_by_id(idx=idx).text

    @step('Проверка наличия у элемента с id - {idx}, текста - {text}')
    def assert_text(self, idx, text):
        assert self.get_text(idx=idx) == text

    @step('Проверка наличия у элемента с id - {idx}, текста - {text}')
    def smart_assert_text(self, idx, text, timeout=10):
        current_text = ''
        is_asserts = False
        for i in range(0, timeout * 10):
            try:
                current_text = self.get_text(idx=idx)
                if current_text.lower() == text.lower():
                    is_asserts = True
                    break
                raise Exception()
            except BaseException:
                from time import sleep
                sleep(0.1)
        if not is_asserts:
            assert False, f'Найденный текст - "{current_text}" не совпадает с ожидаемым текстом - "{text}"'
