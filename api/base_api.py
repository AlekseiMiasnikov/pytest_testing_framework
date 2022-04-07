from allure import step
from requests import Session, get


class BaseApi:
    def __init__(self, api_base_url, session=Session()):
        self.api_base_url = api_base_url
        self.session = session

    @step('Отправка GET запроса на url - {url}')
    def send_get(self, url='/'):
        try:
            return get(url=f'{self.api_base_url}/{url}', verify=False).json()
        except Exception as e:
            print('Непредвиденная ошибка:', e)

    @step('Отправка POST запроса на url - {url}')
    def send_post(self, data=None, url='/', files=None, auth=None):
        for _ in range(0, 100):
            if data is None:
                data = {}
            if files is None:
                files = {}
            try:
                is_json = isinstance(data, dict)
                response = self.session.post(
                    url=f'{self.api_base_url}/{url}',
                    json=data if is_json else None,
                    data=None if is_json else data,
                    files=files,
                    verify=False,
                    auth=auth
                )
                if response.content != '':
                    return response.json()
            except Exception as e:
                print('Непредвиденная ошибка:', e)
