# Pytest testing framework

## Разработка и запуск тестов

1. При активации параметра `ALLURE_FOR_TESTRAIL_ENABLED` следует запускать тесты, добавляя в команду запуска
   тестов: `--alluredir=raw_reports`.
2. Для автоматического выставления `Type: Automated`, `Automated Type: API/GUI` для тест-кейса в `TestRail` авто-тесты
   для UI должны в пути проекта иметь папку с названием `UI` или `ui`, а для API `API` или `ui`. Информация, в какой
   папке лежат тесты берётся из `allure` отчёта, поэтому, для автоматического выставления нужно запускать авто-тесты,
   добавляя `--alluredir=raw_reports`, а так же должны быть активны параметры `ALLURE_FOR_TESTRAIL_ENABLED`
   и `TESTRAIL_ENABLED`.
3. Для автоматической генерации тест-кейса в `TestRail` нужно добавить сверху
   теста: `@TestRail.suite('Название_группы')`
   , где Название_группы - это группа из TestRail. При первом запуске сгенерируется тест-кейс с названием, описанием и
   шагами, а так же у авто-теста в коде автоматически проставится id тест-кейса в `TestRail`. При запуске авто-теста
   нужно добавить команду `--alluredir=raw_reports`, а так же должны быть активны
   параметры `ALLURE_FOR_TESTRAIL_ENABLED` и `TESTRAIL_ENABLED`.

## Docker

1. Docker можно запустить в файле `Dockerfile`.
2. Если не запускается, в `cmd` запустить команду `wsl`, ввести свой пароль и запустить активацию докера. У вас будет
   свой путь, но пример команды: `sudo /etc/init.d/docker start`
3. После внесения правок в коде тестов удалить старый `Image` во вкладке `Services` в PyCharm, если нужно произвести
   новый запуск в Docker.

## GitLab CI

1. Настроить CI для GitLab можно с помощью файла `.gitlab-ci.yml`.
2. `flake8 .` - статический анализатор кода
3. `unittests` - unit-тесты для проверки методов ядра фреймворка на базе Pytest

## Appium

1. Пример для Android apk находятся в `files/apk/` ➔ переместить на локальный диск и указать это в `mobile_config` в
   файле `utils`
2. Должен быть включен эмулятор устройства в Android Studio и необходимый конфиг вписать в фикстуру в
   папке `fixtures_ui`

# Команды

Пример:

````
pytest --alluredir=raw_reports -n 16 --mode selenoid
````

`pytest` - локальный запуск всех тестов

`pytest --alluredir=raw_reports` - локальный запуск всех тестов с сохранением статусов для отчета `allure`.
Параметр `ALLURE_FOR_TESTRAIL_ENABLED` должен быть со значением `1` чтобы отчёты в папке `reports` не были автоматически
очищены.

`pytest -m dev` - локальный запуск теста для разработки (Добавить над названием теста `@mark.dev` и сделать
импорт `from pytest import mark`)

`pytest -n 16` - локальный запуск всех тестов в несколько потоков, где цифра определяет число потоков

`pytest --mode selenoid` - запуск всех тестов на `selenoid`

`allure serve reports` - генерация отчета `allure`

`pip install -r requirements.txt` - установка всех пакетов из файла `requirements.txt`, которые удалось определить

`pip freeze > requirements.txt` - сохранение установленных пакетов в файл `requirements.txt`

`flake8 .` - запуск статического анализатора кода

# Описание параметров

> [pytest.ini]

Пример:

````
    environment=test
    ALLURE_DIR=raw_reports
    ALLURE_FOR_TESTRAIL_ENABLED=0
    TESTRAIL_ENABLED=0
    TESTRAIL_AUTOCLOSE_TESTRUN=1
    TESTRAIL_EMAIL=root@gmail.com
    TESTRAIL_PASSWORD=
    DB_POSTGRESQL_USER_EXAMPLE=
    DB_POSTGRESQL_PASSWORD_EXAMPLE=
    DB_ORACLE_USER_EXAMPLE=
    DB_ORACLE_PASSWORD_EXAMPLE=
    TESTRAIL_URL=
    TESTRAIL_PROJECT_ID=
    TESTRAIL_TITLE_RUN=root
    TESTRAIL_MILESTONE=root
    TESTRAIL_AUTOMATED_TYPE_NONE=0
    TESTRAIL_AUTOMATED_TYPE_API=5
    TESTRAIL_AUTOMATED_TYPE_GUI=6
    TESTRAIL_TYPE_AUTOMATED=3
    TESTRAIL_PASSED_STATUS=1
    TESTRAIL_FAILED_STATUS=5
    TESTRAIL_BLOCKED_STATUS=2
    TESTRAIL_BROWSER=1
````

`environment` - указание окружения, должно соответствовать верхнему ключу из файла `config.json` ➔ `test`

`ALLURE_DIR` - название папки, откуда считывает информацию параметр `ALLURE_FOR_TESTRAIL_ENABLED`. Указывать эту папку
при выполнении команды с сохранением отчёта `allure` командой `pytest --alluredir=reports`

`ALLURE_FOR_TESTRAIL_ENABLED ` - считывание информации с сохранённого отчёта `allure`. Копирует содержимое
папки `reports` и считывает данные из неё, а после выставления статусов временная папка удаляется.   (`0` -
выключено, `1` - включено). При включении параметра тест-кейсы в `TestRail` будут иметь шаги, название шагов, статусы
шагов, скриншот последнего шага в случаи ошибки и затраченное время шага. При этом параметры `TESTRAIL_ENABLED`
и `TESTRAIL_AUTOCLOSE_TESTRUN`
должны быть включены и в команде запуска тестов нужно добавлять: `pytest --alluredir=reports` для корректной работы
этого параметра. Так же автоматически проставятся статусы `Automated` и `API/GUI` - в зависимости, в какой папке
находится авто-тест. Для генерации `@TestRail.id('id_testcase')` над авто-тестом должен быть
написан `@TestRail.suite('suite_in_testrail')`.

`TESTRAIL_ENABLED` - активность интеграции с `TestRail` (`0` - выключено, `1` - включено)

`TESTRAIL_AUTOCLOSE_TESTRUN ` - автоматическое закрытие созданного тестового прогона (`0` - выключено, `1` - включено).
Если параметр `1`, то в прогон будут добавлены только автоматизированные кейсы. Если `0`, то добавятся все существующие
тест-кейсы и прогон не будет закрыт. Если параметр `1` и параметр `ALLURE_FOR_TESTRAIL_ENABLED` активен, то в тестовый
прогон добавятся только запущенные авто-тесты.

`TESTRAIL_URL` - адрес `TestRail`

`TESTRAIL_EMAIL` - e-mail пользователя `TestRail`, от лица которого будет вестись активность в `TestRail`

`TESTRAIL_PASSWORD` - пароль пользователя `TestRail`

`TESTRAIL_TITLE_RUN` - название тестового прогона

`TESTRAIL_MILESTONE` - название `Milestone` в `TestRail`

`DB_*_USER` - пользователь базы данных

`DB_*_PASSWORD` - пароль пользователя базы данных

#

> [config/config.json]

Пример:

````
{
    "test": {
        "APPLICATION_URL": "http://google.com",
        "API_URL": "https://jsonplaceholder.typicode.com",
        "BROWSER_NAME": "chrome",
        "BROWSER_WINDOW_WIDTH": 1920,
        "BROWSER_WINDOW_HEIGHT": 1080,
        "SELENOID": {
            "ENABLE_VNC": true,
            "ENABLE_VIDEO": false,
            "BROWSER_VERSION": "89.0",
            "HUB": "http://selenoid:4444/wd/hub"
        },
        "APPIUM": {
            "HUB": "http://localhost:4723/wd/hub"
        },
        "TIMEOUT": 60,
        "DB": {
            "DB_TYPE": "mysql",
            "HOST": "localhost",
            "PORT": "3306",
            "DB_NAME": "root"
        }
    }
}
````

`test` - название среды окружения в проекте (`dev`, `test`, `stage`, `preprod`, `prod`)

`APPLICATION_URL` - адрес frontend части web приложения

`API_URL` - адрес backend части web приложения

`BROWSER_NAME` - браузер, в котором будут идти UI тесты

`BROWSER_WINDOW_WIDTH` - ширина окна браузера

`BROWSER_WINDOW_HEIGHT` - высота окна браузера

`SELENOID` - настройки удаленного запуска UI тестов

`ENABLE_VNC` - включение визуализации в `selenoid`

`ENABLE_VIDEO` - включение записи видео теста в `selenoid`

`BROWSER_VERSION` - версия браузера в `selenoid`

`HUB` - адрес `selenoid`, где будут выполнять тесты

`APPIUM` - настройка `HUB` для `appium`

`TIMEOUT` - время ожидания ответа от браузера или api

`DB` - конфигурация базы данных

`DB_TYPE` - тип подключения к базе данных (`mysql`, `postgres`, `oracle`, `mssql`, `sqlite`)

`HOST` - адрес базы данных

`PORT` - порт базы данных

`DB_NAME` - название базы данных

#

> [conftest.py]

Пример:

````
mode = 'local'
settings_config = {}
testrail = TestRail()
testrail_test_run = 0
testrail_api = TestRailAPI(
    url=getenv('TESTRAIL_URL'),
    email=getenv('TESTRAIL_EMAIL'),
    password=getenv('TESTRAIL_PASSWORD'),
    verify=False
) if int(getenv('TESTRAIL_ENABLED')) == 1 else None
temp_files = join(Path(__file__).parent, 'files')

pytest_plugins = get_fixtures()

def pytest_sessionstart():
    ...

def pytest_sessionfinish(session):
    ...

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    ...

def pytest_addoption(parser):
    ...

@pytest.fixture(scope='module')
def browser(pytestconfig):
    ...
````

`mode` - режим работы тестов (`local`, `selenoid`). По умолчанию установлен `local`.

`settings_config` - настройки из файла `config/config.json`

`testrail` - инициализация подключения к `TestRail`

`testrail_test_run` - создание тестового прогона и получение его идентификатора

`testrail_api` - инициализация библиотеки по работе с API `TestRail`

`temp_files` - папка для хранения временных файлов

`pytest_plugins` - получение фикстур из папки `fixtutes`

`pytest_sessionstart` - метод для чтения настроек из файла `config.json` и создание тестового прогона

`pytest_sessionfinish` - метод для закрытия тестового прогона и очистки папки `temp_files`

`pytest_runtest_makereport` - метод для установки различных параметров тест-кейса

`pytest_addoption` - метод для создания параметров командной строки (Указываются параметры для изменения логики запуска
тестов)

`browser` - метод для создания браузера

#

> [fixtures/db.py]

Пример:

````
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart():
    ...

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish():
    ...
````

`pytest_sessionstart` - создание подключения к базе данных

`pytest_sessionfinish` - закрытие подключения к базе данных

#

### Пример структуры авто-теста

> [tests/UI/test_google.py]

Пример:

````
from allure import title, description, suite, parent_suite
from core.utils.testrail import TestRail


@parent_suite('[Pytest][UI]')
@suite('Google')
class TestGoogle:
    @TestRail.suite('Testrail suite name')
    @title('Google: Поиск')
    @description('Проверка поиска через сервис Google')
    @TestRail.id('TESTRAIL_ID')
    def test_google_search(self):
        pass
````

`from allure import title, description, suite, parent_suite` - импорт методов для отчета `allure`

`from core.utils.testrail import TestRail` - импорт метода для добавления id тест-кейса

`parent_suite` - верхнеуровневая папка в отчете `allure`

`suite` - папка в сгенерированном отчёте `allure`

`class TestGoogle` - группировка тестов

`@TestRail.suite('')` - название секции, в которой хранятся тест-кейсы. При отсутствии `@TestRail.id('')` при локальном
запуске `id` автоматически добавится над авто-тестом, а так же в `TestRail` сгенерируется тест-кейс, указанный в `suite`

`@title('')` - наименование теста в сгенерированном отчёте `allure`

`@description('')` - описание действий теста в сгенерированном отчёте `allure`

`@TestRail.id('')` - идентификатор тест-кейса в `TestRail`

`def test_google_search(self):` - название теста

#

> [core/db/db.py]

Пример:

````
BASE = declarative_base()

class DB:
    def __init__(self, session=None):
        ...

    def _connection(self, environment):
        ...

    def create_session(self, environment):
        ...

    def get(self, table_name: any, limit: int = 0, offset: int = 0):
        ...

    def create(self, query_object: any):
        ...

    def create_all(self, query_object: any):
        ...

    def update(self, table_name: any, condition: dict, update_value: dict):
        ...

    def delete(self, table_name: any, condition: dict):
        ...

    def execute(self, query: str):
        ...

    def get_by(self, table_name: any, condition: dict, limit: int = 0, offset: int = 0):
        ...

    def close(self):
        ...

class DBHelper:
    def column(self, column, dimensions=1, *args, **kwargs):
        ...
````

`BASE` - инициализация базы данных

`DB` - основной класс по работе с базой данных

`__init__` - конструктор подключения к базе данных

`_connection` - приватный метод для подключения к базе данных

`create_session` - метод для создания сессии

`get` - метод для получения записи

`create` - метод для добавления одной записи

`create_all` - метод для добавления нескольких записей

`update` - метод для обновления записи

`delete` - метод для удаления записи

`execute` - метод для выполнения чистого SQL-выражения

`get_by` - метод для получения записи по условию

`get_by_id` - метод для получения записи по id

`close` - метод для закрытия сессии

`DBHelper` - класс для создания типа поля в модели

`column` - метод для создания типа поля

#

> [core/utils/testrail.py]

Пример:

````
class TestRail:

    def id(*ids: str) -> mark:
        ...

    def def suite(*name: str) -> mark:
        ...
        
    def _get_status(self, tr: TestRailAPI, case_id: int, test_run_id: int) -> int:
        ...

    def _get_milestone_id(self, tr: TestRailAPI):
        ...

    def _get_test_runs(self, tr: TestRailAPI, name: str):
        ...
    
    def _get_test_case_ids(self):
        ...
    
    def _copy_files(self, source_folder, destination_folder):
        ...
    
    def _get_allure_result(self):
        ...
    
    def _get_comment(self, result, mode):
        ...

    def _get_path(self, data):
        ...
    
    def _get_suites(self, tr: TestRailAPI, name: str):
        ...
    
    def _add_testrail_id_in_file_before_test(self, id: int, full_name: str):
        ...
         
    def _get_test_cases_by_suite(self, tr: TestRailAPI, suite_id: int, case_name: str):
        ...
    
    def _update_test_case(self, tr: TestRailAPI, case: dict, case_params: list):
        ...
    
    def _create_test_case(self, tr: TestRailAPI, case_info: list):
        ...
    
    def _get_test_type(self, value):
        ...
    
    def set_automation_status(self, tr: TestRailAPI, case_id: int, automated_type: int):
        ...z
    
    def set_automation_status(self, tr: TestRailAPI, case_id: int, automated_type: int):
        ...
        
    def create_test_run(self, tr: TestRailAPI) -> int:
        ...
    
    def close_test_run(self, tr: TestRailAPI, run_id: int):
        ...
    
    def set_status(self, tr: TestRailAPI, data: dict):
        ...
        
    def formatted_time_for_testrail(self, seconds):
        ...
    
    def set_statuses(self, tr, data):
        ...
````

`TestRail` - класс для работы с API `TestRail`

`id` - присвоение идентификатора тест-кейса

`suite` - присвоении секции тест-кейсу

`_get_status` - приватный метод для получения статуса текущего тест-кейса

`_get_milestone_id` - приватный метод для получения идентификатора созданного `Milestone`

`_get_test_runs` - приватный метод для получения идентификатора созданного прогона

`_get_test_case_ids` - приватный метод для получения списка идентификаторов, указанных в тестах

`_copy_files` - приватный метод для копирования папки reports с последующим её удалением

`_get_allure_result` - приватный метод чтения файлов отчёта `allure`

`_get_comment` - приватный метод для создания каркаса всех данных в комментарий

`_get_path` - приватный метод для получения пути к allure, если в пути найден `buildagent` выбирается иной путь
для `TeamCity`

`_get_suites` - приватный метод для получения секций из `TestRail`

`_add_testrail_id_in_file_before_test` - приватный метод для добавления над авто-тестом `id` созданного тест-кейса

`_get_test_cases_by_suite` - приватный метод для получения тест-кейсов в определенной секции из `TestRail`

`_update_test_case` - приватный метод для обновления данных/корректной записи параметров в параметризованных тест-кейсах

`_create_test_case` - приватный метод для создания тест-кейса в `TestRail`

`_get_test_type` - приватный метод для получения `Type` и `Automated Type` из `TestRail`

`set_automation_status` - метод для выставления `Type` и `Automated Type` тест-кейсу в `TestRail`

`create_test_run` - метод для создания прогона

`close_test_run` - метод для закрытия тестового прогона

`set_status` - метод для установки статуса тест-кейса

`set_automation_status` - метод для автоматического выставления `Type: Automated`, `Automated Type: API/GUI` для
тест-кейса в `TestRail`. Авто-тесты для UI должны в пути проекта иметь папку с названием `UI` или `ui`, а для API `API`
или `ui`. Информация в какой папке лежат тесты берётся из `allure` отчёта, поэтому для автоматического выставления нужно
запускать авто-тесты, добавляя `--alluredir=reports`

`formatted_time_for_testrail` - метод для форматирования времени в `1h 10m 5s`

`set_statuses` - метод использования данных из отчёта `allure` для выставления различных значений в тест-кейс, а так же
прикрепления скриншотов и логов

#

> [core/utils/allure_wrapper.py]

`step` - аналог метода `step` из `allure`. Добавляет скриншоты на каждый шаг в `allure`. Использовать для UI авто-тестов

#

> [core/utils/helpers.py]

````
def get_settings(environment):
    ...

def formatted_time_for_testrail(seconds):
    ...

def get_count_tests(reporter):
    ...

def get_fixtures():
    ...
````

`get_settings` - метод для получения настроек из файла `config/config.json`

`formatted_time_for_testrail` - метод для форматирования времени в `1h 10m 5s`

`get_count_tests` - метод для получения общего числа пройденных тестов

`get_fixtures` - метод для получения файлов с фикстурами

#

> [core/utils/helpers.py]

````
@step('Проверка соответсвия приходящего JSON')
def asserts(actual_data, asserts_data):
````

`asserts` - метод для проверки соответствия приходящего JSON
