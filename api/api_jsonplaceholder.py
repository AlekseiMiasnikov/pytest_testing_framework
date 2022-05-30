from allure import step
from api.base_api import BaseApi


class ApiJsonplaceholder(BaseApi):
    @step('GET-запрос. Получение данных. URL: https://jsonplaceholder.typicode.com//posts/1')
    def jsonplaceholder_get(self):
        return self.send_get(url='posts/1')

    @step('POST-запрос. Создание ресурса. URL: https://jsonplaceholder.typicode.com//posts/')
    def jsonplaceholder_post(self, data):
        return self.send_post(url='posts', data=data, is_json=True)
