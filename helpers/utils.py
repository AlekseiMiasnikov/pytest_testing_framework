from allure import step


@step('Проверка соответствия приходящего JSON')
def asserts(actual_data: list, asserts_data: list):
    for key, item in enumerate(asserts_data):
        if isinstance(item, dict):
            for value in item.keys():
                if str(value).lower() in dict(actual_data[key]).keys() \
                        and str(value).lower() in dict(asserts_data[key]).keys():
                    assert actual_data[key][str(value).lower()] == asserts_data[key][str(value).lower()], \
                        f'Не найден {str(value).lower()} в списке {item}'
        elif isinstance(asserts_data[item], dict):
            for data in asserts_data[item]:
                assert actual_data[item][data] == asserts_data[item][data]
        else:
            assert actual_data[item] == asserts_data[item]
