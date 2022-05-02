import json
import os
import shutil
from os import getcwd
from os.path import join
from pathlib import Path

from pytest import PytestWarning


def get_settings(environment):
    CONFIG_PATH = join(get_current_folder(folder='config'), 'config.json')
    with open(CONFIG_PATH) as data:
        config = json.load(data)
        return config[environment]


def copy_files(source_folder, destination_folder):
    if not os.path.isdir(destination_folder):
        os.makedirs(destination_folder)
    for file_name in os.listdir(source_folder):
        source = join(source_folder, file_name)
        destination = join(destination_folder, file_name)
        if os.path.isfile(source):
            shutil.copy(source, destination)


def formatted_time_for_testrail(seconds):
    hour = seconds // 3600
    seconds = seconds % 3600
    minutes = seconds // 60
    seconds = seconds % 60
    if hour != 0 and minutes != 0 and seconds != 0:
        return f'{hour}h {minutes}m {seconds}s'
    if minutes != 0 and seconds != 0:
        return f'{minutes}m {seconds}s'
    return f'{seconds}s'


def get_count_tests(reporter):
    tests_count = 0
    for status in ['passed', 'failed', 'xfailed', 'skipped']:
        if status in reporter.stats:
            tests_count += len(reporter.stats[status])
    return tests_count


def get_current_folder(folder: str) -> str:
    current = getcwd()

    def find_folder(path: str or Path) -> str:
        for _, f, _ in os.walk(path):
            if folder in f:
                return join(path, folder)
        else:
            return find_folder(path=Path(path).parent)

    return find_folder(path=current)


def get_fixtures():
    files_list = []
    for root, dirs, files in os.walk(get_current_folder(folder='fixtures')):
        for file in files:
            if '.pyc' not in file:
                root_folder = root[root.find('fixtures'):].replace('\\', '.').replace('/', '.')
                file_name = file[:len(file) - 3]
                files_list.append(f'{root_folder}.{file_name}')
    if len(files_list) == 0:
        raise PytestWarning('Не поддерживаемый запуск')
    return files_list
