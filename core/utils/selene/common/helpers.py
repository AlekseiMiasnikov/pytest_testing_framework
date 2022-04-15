from typing import Union, Tuple, List

from selenium.webdriver.common.by import By


def as_dict(o, skip_empty=True):
    return (
        {
            k: v
            for k, v in o.__dict__.items()
            if not (skip_empty and v is None) and not k.startswith('_')
        }
        if o
        else {}
    )


def to_by(selector_or_by: Union[str, tuple]) -> Tuple[str, str]:
    if isinstance(selector_or_by, tuple):
        return selector_or_by
    if isinstance(selector_or_by, str):
        return (
            (By.XPATH, selector_or_by)
            if (
                    selector_or_by.startswith('/')
                    or selector_or_by.startswith('./')
                    or selector_or_by.startswith('..')
                    or selector_or_by.startswith('(')
            )
            else (By.CSS_SELECTOR, selector_or_by)
        )
    raise TypeError(
        'selector_or_by should be str with CSS selector or XPATH selector or Tuple[by:str, value:str]'
    )


def flatten(list_of_lists: List[list]) -> list:
    return [
        item
        for sublist in list_of_lists
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]


def dissoc(associated: dict, *keys: str) -> dict:
    return {k: v for k, v in associated.items() if k not in keys}


def on_error_return_false(no_args_predicate):
    try:
        return no_args_predicate()
    except Exception:
        return False


def is_absolute_url(relative_or_absolute_url: str) -> bool:
    url = relative_or_absolute_url.lower()
    return (
            url.startswith('http:')
            or url.startswith('https:')
            or url.startswith('file:')
            or url.startswith('about:')
            or url.startswith('data:')
    )
