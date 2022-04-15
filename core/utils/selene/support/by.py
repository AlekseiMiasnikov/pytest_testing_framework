import warnings

from selenium.webdriver.common.by import By


def css(selector):
    return By.CSS_SELECTOR, selector


def xpath(selector):
    return By.XPATH, selector


def id(attribute_value):
    return By.ID, attribute_value


def name(attribute_value):
    return By.NAME, attribute_value


def link_text(value):
    return By.LINK_TEXT, value


def partial_link_text(value):
    return By.PARTIAL_LINK_TEXT, value


def _escape_text_quotes_for_xpath(text):
    return 'concat("", "%s")' % (str("\", '\"', \"".join(text.split('"'))))


def text(value):
    return xpath(
        './/*[text()[normalize-space(.) = '
        + _escape_text_quotes_for_xpath(value)
        + ']]'
    )


def partial_text(value):
    return xpath(
        './/*[text()[contains(normalize-space(.), '
        + _escape_text_quotes_for_xpath(value)
        + ')]]'
    )


def be_following_sibling(with_tag: str = '*'):
    warnings.warn(
        'deprecated; use xpath explicitly to not hide complexity in workaround',
        DeprecationWarning,
    )
    return xpath(f'./following-sibling::{with_tag}')


def be_parent():
    warnings.warn(
        'deprecated; use xpath explicitly to not hide complexity in workaround',
        DeprecationWarning,
    )
    return xpath('..')


def be_first_child(with_tag: str = '*'):
    warnings.warn(
        'deprecated; use xpath explicitly to not hide complexity in workaround',
        DeprecationWarning,
    )
    return xpath(f'./{with_tag}[1]')
