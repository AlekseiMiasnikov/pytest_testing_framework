import os
from datetime import datetime
from json import loads
from os import getenv
from os.path import join, isfile
from pathlib import Path
from platform import system
from typing import Optional, Any

from pytest import mark
from testrail_api import TestRailAPI


class TestRail:
    @staticmethod
    def id(*ids: str) -> mark:
        return mark.testrail_ids(ids=ids)

    @staticmethod
    def suite(*name: str) -> mark:
        return mark.testrail_suite(name=name)

    def _get_status(self, tr: TestRailAPI, case_id: int, test_run_id: int) -> Optional[int]:
        if case_id == 0:
            return
        case = tr.results.get_results_for_case(
            run_id=int(test_run_id),
            case_id=int(case_id),
            limit=1
        )
        if len(case) == 0:
            return 0
        return int(case[0]['status_id'])

    def _get_milestone_id(self, tr: TestRailAPI) -> int:
        mls = tr.milestones.get_milestones(project_id=int(getenv('TESTRAIL_PROJECT_ID')))
        for ml in mls:
            if ml['name'] == str(getenv('TESTRAIL_MILESTONE')):
                return ml['id']

    def _get_test_runs(self, tr: TestRailAPI, name: str) -> None:
        for run in tr.runs.get_runs(project_id=int(getenv('TESTRAIL_PROJECT_ID')), is_completed=False):
            if name in run['name']:
                return run['id']
        return None

    def _get_test_case_ids(self) -> list:
        test_case_ids = []
        tests = self._get_path({'is_tests': True, 'nested_path': 'tests'})
        for root, dirs, files in os.walk(tests, topdown=False):
            for name in files:
                if name.split('.')[-1] == 'pyc':
                    continue
                file = open(os.path.join(root, name), 'r', encoding='UTF-8')
                text = str(file.read())
                while text.find("@TestRail.id('") != -1:
                    start_with = text.find("@TestRail.id('") + 15
                    id = text[start_with::].split("')")[0]
                    if id != '' and len(id) > 2:
                        test_case_ids.append(int(id))
                    text = text[start_with::]
        return test_case_ids

    def _get_allure_result(self) -> dict:
        results = []
        testrail_ids = []
        files = self._get_path({'is_nested_path': False})
        for root, _, files in os.walk(files, topdown=False):
            for file in files:
                if 'result.json' in file:
                    with open(os.path.join(root, file), 'r', encoding='UTF-8') as f:
                        results.append(loads(f.read()))
        start = "testrail_ids(ids=('C"
        end = "',))"
        for value in results:
            if 'labels' in value.keys():
                for label in value['labels']:
                    if str(label['value']).startswith(start):
                        testrail_ids.append(label['value'][len(start):-len(end)])
        return {
            'results': results,
            'testrail_ids': testrail_ids
        }

    def _get_comment(self, result, mode) -> str:
        comment = [f'**Режим запуска**: {"Локальный" if mode == "local" else "Удаленный"}\n\n', ]
        if result["case_name"] != '':
            comment.append(f'**Название теста**: {result["case_name"]}\n')
        if result["case_description"] != '':
            comment.append(f'**Описание**: {result["case_description"]}\n')
        if result["case_status"] != '':
            comment.append(f'**Статус теста**: {result["case_status"]}\n\n')
        if len(result['params']):
            comment.append(''.join(result['params']))
        if len(result['steps']):
            comment.append('**Шаги**:\n\n')
        for key, item in enumerate(result['steps']):
            comment.append(f'{key + 1}.\tНазвание: {item["name"]}\n')
            comment.append(f'\tСтатус: {item["status"]}\n')
            comment.append(f'\tВремя выполнения: {item["time"]}\n\n')
        if result['error']['message'] != '' and result['error']['trace'] != '':
            comment.append('\n\n\n##Ошибка:\n\n')
            comment.append(f'Сообщение: {result["error"]["message"]}\n\n')
            comment.append(f'Расположение: \n`{result["error"]["trace"]}`\n\n')
        # if len(result['attachments']):
        #     comment.append('\nЛоги:\n')
        # for key, item in enumerate(result['attachments']):
        #     comment.append(f'{key + 1}.\t{item["name"]}\n')
        return ''.join(comment)

    def _get_path(self, data) -> str:
        is_tests = data.get('is_tests', False)
        is_nested_path = data.get('is_nested_path', False)
        nested_path = data.get('nested_path', '/')
        files = join(Path(__file__).parent.parent.parent.parent.parent.parent.parent, nested_path)
        if 'buildagent' in str(Path(__file__)).lower():
            root_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent
            if is_nested_path:
                return f'{join(root_path, getenv("ALLURE_DIR"))}/{nested_path}'
            return join(root_path, nested_path)
        if system().lower() in ['linux', 'darwin']:
            if is_tests:
                return join('/app', nested_path)
            else:
                if is_nested_path:
                    return f'{join("/app", getenv("ALLURE_DIR"))}/{nested_path}'
                else:
                    return f'{join("/app", getenv("ALLURE_DIR"))}'
        if system().lower() == 'windows':
            if is_tests:
                return files
            else:
                root_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent
                if is_nested_path:
                    return f'{join(root_path, getenv("ALLURE_DIR"))}/{nested_path}'
                else:
                    return f'{join(root_path, getenv("ALLURE_DIR"))}'
        return files

    def _get_suites(self, tr: TestRailAPI, name: str) -> Optional[dict[str, Any]]:
        for suite in tr.sections.get_sections(project_id=int(getenv('TESTRAIL_PROJECT_ID'))):
            if str(suite['name']).lower() == name.lower():
                return {
                    'id': suite['id'],
                    'suite_id': suite['suite_id'],
                }
        suite = tr.sections.add_section(project_id=int(getenv('TESTRAIL_PROJECT_ID')), name=name)
        return {
            'id': suite['id'],
            'suite_id': suite['suite_id'],
        }

    def _add_testrail_id_in_file_before_test(self, id: int, full_name: str):
        test_name = full_name.split('#')[-1]
        class_name = full_name.split('#')[0].split('.')[-1]
        full_test_path = '/'.join(full_name.split('#')[0].replace('.', '/').split('/')[1:-1]) \
            if system().lower() in ['linux', 'darwin'] else \
            '\\'.join(full_name.split('#')[0].replace('.', '/').split('/')[1:-1])
        tests = self._get_path({'is_tests': True, 'nested_path': 'tests'})
        readed_files = []
        for root, dirs, files in os.walk(tests, topdown=False):
            for name in files:
                if name.split('.')[-1] == 'pyc':
                    continue
                file = open(os.path.join(root, name), 'r', encoding='UTF-8')
                text = str(file.read())
                file.close()
                if class_name in text and test_name in text:
                    readed_name = f'{full_test_path}/{class_name}/{test_name}'
                    if readed_name in readed_files:
                        continue
                    readed_files.append(readed_name)
                    with open(f'{tests}/{full_test_path}.py', 'r+', encoding='UTF-8') as file:
                        src = file.readlines()
                        file.seek(0)
                        for line in src:
                            test__name = str(line).split('def ')[1].split('(')[0] if test_name in line else ''
                            if line.find(test_name) != -1 and test__name == test_name:
                                file.write(f"    @TestRail.id('C{id}')\n{line}")
                            else:
                                file.write(line)

    def _get_test_cases_by_suite(self, tr: TestRailAPI, suite_id: int, section_id: int, case_name: str) -> dict:
        cases = tr.cases.get_cases(
            project_id=int(getenv('TESTRAIL_PROJECT_ID')),
            suite_id=suite_id,
            section_id=section_id
        )
        data = {
            'result': False,
            'data': {}
        }
        for case in cases:
            if 'title' not in case:
                return data
            if str(case['title']).lower() == case_name.lower():
                return {
                    'result': True,
                    'data': case
                }
        return data

    def _get_custom_result_field(self, tr: TestRailAPI) -> dict:
        fields_list = {}
        fields = tr.result_fields.get_result_fields()
        for field in fields:
            if str(field['system_name']).startswith('custom_'):
                fields_list[field['system_name']] = field['configs'][0]['options'][
                    'default_value'] if 'default_value' in field['configs'][0]['options'].keys() else ""
        return fields_list

    def _get_custom_case_field(self, tr: TestRailAPI) -> dict:
        fields_list = {}
        fields = tr.case_fields.get_case_fields()
        for field in fields:
            if str(field['system_name']).startswith('custom_'):
                fields_list[field['system_name']] = field['configs'][0]['options'][
                    'default_value'] if 'default_value' in field['configs'][0]['options'].keys() else ""
        return fields_list

    def _update_test_case(self, tr: TestRailAPI, case: dict, case_params: list):
        custom_steps = []
        if 'custom_steps' not in dict(case).keys():
            return
        params = str(case['custom_steps']).split('\n\n\n')[0]
        params_rest = str(case['custom_steps']).split('\n\n\n')[-1]
        params_header = str(params).split('\n|||')[0]
        params_data = str(params).split('\n|||')[-1]
        custom_steps.append(params_header)
        custom_steps.append('\n|||')
        custom_steps.append(f'{params_data}\n')
        custom_steps.append(''.join(case_params))
        custom_steps.append('\n\n\n')
        custom_steps.append(params_rest)
        tr.cases.update_case(case_id=case['id'], custom_steps=''.join(custom_steps))

    def _create_test_case(self, tr: TestRailAPI, case_info: list, custom_fields: dict):
        result = {
            'suite_name': None,
            'title': None,
            'description': None,
            'steps': [],
            'params': []
        }
        start = "testrail_suite(name=('"
        end = "',))"
        if 'labels' in dict(case_info).keys():
            for label in dict(case_info).get('labels'):
                if str(label['value']).startswith(start):
                    result['suite_name'] = label['value'][len(start):-len(end)]
        if result['suite_name'] is None:
            return
        suite_id = self._get_suites(tr=tr, name=result['suite_name'])
        if suite_id['id'] is None:
            return
        if 'name' not in dict(case_info).keys():
            return
        result['title'] = dict(case_info).get('name')
        if 'description' not in dict(case_info).keys():
            return
        result['description'] = dict(case_info).get('description')
        if 'parameters' in dict(case_info).keys():
            result['steps'].append('**Параметры**:\n')
            result['steps'].append('|||:Название|:Значение\n')
            for parametr in dict(case_info).get('parameters'):
                result['steps'].append(f'|| {parametr["name"]} | {parametr["value"]}\n')
                result['params'].append(f'|| {parametr["name"]} | {parametr["value"]}\n')
        if 'steps' not in dict(case_info).keys():
            return
        if len(dict(case_info).get('steps')) == 0:
            return
        if 'steps' in dict(case_info).keys():
            result['steps'].append('\n\n**Шаги**:\n')
        for key, step in enumerate(dict(case_info).get('steps')):
            result['steps'].append(f'{key + 1}. {step["name"]}\n')
        if 'fullName' not in dict(case_info).keys():
            return
        case = self._get_test_cases_by_suite(
            tr=tr,
            suite_id=suite_id['suite_id'],
            section_id=suite_id['id'],
            case_name=result['title']
        )
        if case['result']:
            self._update_test_case(tr=tr, case=case['data'], case_params=result['params'])
            return
        for field in dict(custom_fields).keys():
            if field == 'custom_preconds':
                custom_fields[field] = result['description']
            if field == 'custom_steps':
                custom_fields[field] = ''.join(result['steps'])
        created_case = tr.cases.add_case(
            section_id=suite_id['id'],
            title=result['title'],
            **custom_fields
        )
        if 'fullName' in dict(case_info).keys():
            automated_type = self._get_test_type(value=dict(case_info).get('fullName'))
            self.set_automation_status(tr=tr, case_id=created_case['id'], automated_type=automated_type)
        self._add_testrail_id_in_file_before_test(id=created_case['id'], full_name=dict(case_info).get('fullName'))

    def _get_test_type(self, value) -> int:
        return int(getenv('TESTRAIL_AUTOMATED_TYPE_API')) if 'api' in str(value).lower() \
            else int(getenv('TESTRAIL_AUTOMATED_TYPE_GUI')) if 'ui' in str(value).lower() \
            else int(getenv('TESTRAIL_AUTOMATED_TYPE_NONE'))

    def set_automation_status(self, tr: TestRailAPI, case_id: int, automated_type: int):
        if system().lower() in ['linux', 'darwin']:
            return
        case_info = tr.cases.get_case(case_id=case_id)
        if int(case_info['type_id']) != int(getenv('TESTRAIL_TYPE_AUTOMATED')):
            tr.cases.update_case(case_id=case_id, type_id=getenv('TESTRAIL_TYPE_AUTOMATED'))
        if int(case_info['custom_automation_type']) != int(getenv('TESTRAIL_AUTOMATED_TYPE_API')) \
                and int(automated_type) == int(getenv('TESTRAIL_AUTOMATED_TYPE_API')):
            tr.cases.update_case(case_id=case_id, custom_automation_type=automated_type)
        if int(case_info['custom_automation_type']) != int(getenv('TESTRAIL_AUTOMATED_TYPE_GUI')) \
                and int(automated_type) == int(getenv('TESTRAIL_AUTOMATED_TYPE_GUI')):
            tr.cases.update_case(case_id=case_id, custom_automation_type=automated_type)

    def create_test_run(self, tr: TestRailAPI, testrail_ids=None) -> Optional[dict[int, Any]]:
        if testrail_ids is None:
            testrail_ids = []
        case_ids = []
        date = datetime.today().strftime('%d.%m.%Y')
        time = datetime.today().strftime('%H:%M:%S')
        name = f"{getenv('TESTRAIL_TITLE_RUN')} {date} {time}"
        ml = self._get_milestone_id(tr=tr)
        if not ml:
            raise ValueError('Milestone с указаным именем не найден')
        lasted_test_run = self._get_test_runs(tr=tr, name=f"{getenv('TESTRAIL_TITLE_RUN')} {date}")
        if lasted_test_run is not None:
            return lasted_test_run
        if int(getenv('ALLURE_FOR_TESTRAIL_ENABLED')) == 0:
            case_ids = self._get_test_case_ids()
        elif int(getenv('ALLURE_FOR_TESTRAIL_ENABLED')) == 1:
            case_ids = testrail_ids
        return tr.runs.add_run(
            project_id=int(getenv('TESTRAIL_PROJECT_ID')),
            name=name,
            milestone_id=ml,
            case_ids=case_ids,
            include_all=len(case_ids) == 0
        )['id']

    def close_test_run(self, tr: TestRailAPI, run_id: int):
        if tr.runs.get_run(run_id=run_id)['is_completed']:
            return
        tr.runs.close_run(run_id=run_id)

    def set_status(self, tr: TestRailAPI, data: dict):
        test_run_id = data['test_run_id']
        case_id = int(str(data['case_id'][1:]))
        if test_run_id is None:
            return
        if self._get_status(tr, case_id, test_run_id) == getenv('TESTRAIL_FAILED_STATUS'):
            print(f'Тест кейс с ID {data["case_id"]} уже находится в статусе Failed')
            return
        result = tr.results.add_result_for_case(
            run_id=int(test_run_id),
            case_id=int(case_id),
            status_id=int(data['status']),
            elapsed=data['elapsed'],
            comment=data['comment']
        )
        if data.get('screenshot') is not None:
            tr.attachments.add_attachment_to_result(result["id"], data['screenshot'])

    def formatted_time_for_testrail(self, seconds) -> str:
        hour = round(seconds // 3600)
        seconds = round(seconds % 3600)
        minutes = round(seconds // 60)
        seconds = round(seconds % 60)
        if hour != 0 and minutes != 0 and seconds != 0:
            return f'{hour}h {minutes}m {seconds}s'
        if minutes != 0 and seconds != 0:
            return f'{minutes}m {seconds}s'
        if seconds == 0:
            return '0.1s'
        return f'{seconds}s'

    def set_statuses(self, tr, data):
        raw_data = self._get_allure_result()
        custom_case_fields = self._get_custom_case_field(tr=tr)
        custom_result_fields = self._get_custom_result_field(tr=tr)
        custom_browser = getenv('TESTRAIL_BROWSER')
        if custom_browser is not None:
            custom_browser = int(custom_browser)
        for field in custom_result_fields.keys():
            if field == 'custom_browser' and custom_browser is not None:
                custom_result_fields[field] = custom_browser
        if int(getenv("ALLURE_FOR_TESTRAIL_ENABLED")) == 1 and len(raw_data['testrail_ids']) > 0:
            data['test_run_id'] = self.create_test_run(tr=tr, testrail_ids=raw_data['testrail_ids'])
        for value in raw_data['results']:
            result = {
                'case_id': None,
                'case_name': '',
                'case_status': '',
                'case_description': '',
                'case_time': 0,
                'steps': [],
                'attachments': [],
                'upload_files': [],
                'params': [],
                'error': {
                    'message': '',
                    'trace': ''
                }
            }
            result['case_name'] = value['name'] if 'name' in value.keys() else ''
            result['case_status'] = value['status']
            result['case_description'] = value['description'] if 'description' in value.keys() else ''
            start = "testrail_ids(ids=('C"
            end = "',))"
            step_data = {}
            if result['case_status'].lower() == 'broken':
                continue
            if 'labels' in value.keys():
                for label in value['labels']:
                    if str(label['value']).startswith(start):
                        result['case_id'] = label['value'][len(start):-len(end)]
            if result['case_id'] is None:
                self._create_test_case(tr=tr, case_info=value, custom_fields=custom_case_fields)
                continue
            if 'statusDetails' in value.keys():
                result['error']['message'] = value['statusDetails']['message']
                result['error']['trace'] = value['statusDetails']['trace']
            if 'parameters' in value.keys():
                result['params'].append('**Параметры**:\n')
                result['params'].append('|||:Название|:Значение\n')
                for parametr in value['parameters']:
                    result['params'].append(f'|| {parametr["name"]} | {parametr["value"]}\n')
            if 'steps' in value.keys():
                for step in value['steps']:
                    image = {
                        'img': None,
                        'name': ''
                    }
                    if 'parameters' in step.keys():
                        for param in step['parameters']:
                            if param['name'] == 'data' and param['value']:
                                step_data['data'] = param['value']
                            if param['name'] == 'expected_data' and param['value']:
                                step_data['expected_data'] = param['value']
                            if param['name'] == 'asserts_data' and param['value']:
                                step_data['asserts_data'] = param['value']
                    if 'attachments' in step.keys():
                        image['img'] = step["attachments"][0]["source"]
                    result['steps'].append({
                        'name': step['name'],
                        'status': step['status'],
                        'time': self.formatted_time_for_testrail(round((step['stop'] - step['start']) / 1000, 3)),
                        'data': step_data,
                        'image': image
                    })
                    result['case_time'] += (step['stop'] - step['start']) / 1000
            result['case_time'] = self.formatted_time_for_testrail(round(result['case_time'], 3))
            if 'attachments' in value.keys():
                for attachment in value['attachments']:
                    result['attachments'].append(attachment["source"])
            for key, val in enumerate(result['steps']):
                if val['status'] == 'passed':
                    continue
                if val['image']['img'] is None:
                    continue
                result['steps'][key]['image']['name'] = val["image"]["img"]
                result['upload_files'].append(
                    self._get_path({'is_tests': True, 'nested_path': f'{getenv("ALLURE_DIR")}/{val["image"]["img"]}'}))
            with open(self._get_path({'is_nested_path': True, 'nested_path': 'mode.txt'}), 'r') as file:
                mode = file.read()
            case_status_id_current = int(self._get_status(tr, int(result['case_id']), int(data['test_run_id'])))
            status_id = getenv('TESTRAIL_PASSED_STATUS')
            if case_status_id_current == int(getenv('TESTRAIL_FAILED_STATUS')) or result['case_status'] == 'failed':
                status_id = getenv('TESTRAIL_FAILED_STATUS')
            if result['case_status'] == 'skipped':
                status_id = getenv('TESTRAIL_BLOCKED_STATUS')
            result_case = tr.results.add_result_for_case(
                run_id=int(data['test_run_id']),
                case_id=int(result['case_id']),
                status_id=status_id,
                elapsed=result['case_time'],
                comment=self._get_comment(result, mode),
                **custom_result_fields
            )
            for file in result['upload_files']:
                if isfile(file):
                    tr.attachments.add_attachment_to_result(result_case["id"], file)
            if 'fullName' in value.keys():
                automated_type = self._get_test_type(value=value['fullName'])
                self.set_automation_status(tr=tr, case_id=result['case_id'], automated_type=automated_type)
        if int(getenv('TESTRAIL_AUTOCLOSE_TESTRUN')) == 1 and len(raw_data['testrail_ids']) > 0:
            self.close_test_run(tr=tr, run_id=data['test_run_id'])
