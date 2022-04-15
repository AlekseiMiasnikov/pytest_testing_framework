from typing import List, Dict, Any, Union

from core.utils.selene.core.entity import Browser, Element, Collection
from core.utils.selene.core.wait import Query


def attribute(name: str) -> Query[Element, str]:
    def fn(element: Element) -> str:
        return element().get_attribute(name)

    return Query(f'attribute {name}', fn)


inner_html = attribute('innerHTML')

outer_html = attribute('outerHTML')

value = attribute('value')

tag: Query[Element, str] = Query(
    'tag name', lambda element: element().tag_name
)

text: Query[Element, str] = Query('text', lambda element: element().text)

location_once_scrolled_into_view: Query[Element, Dict[str, int]] = Query(
    'location once scrolled into view',
    lambda element: element().location_once_scrolled_into_view,
)

size: Union[Query[Element, Dict[str, Any]], Query[Collection, int]] = Query(
    'size',
    lambda entity: entity().size
    if isinstance(entity, Element)
    else len(entity()),
)

location: Query[Element, Dict[str, int]] = Query(
    'location', lambda element: element().location
)

rect: Query[Element, Dict[str, Any]] = Query(
    'rect', lambda element: element().rect
)

screenshot_as_base64: Query[Element, Any] = Query(
    'screenshot as base64', lambda element: element().screenshot_as_base64
)

screenshot_as_png: Query[Element, Any] = Query(
    'screenshot as png', lambda element: element().screenshot_as_png
)


def screenshot(filename: str) -> Query[Element, bool]:
    def fn(element: Element) -> str:
        return element().screenshot(filename)

    return Query(f'screenshot {filename}', fn)


internal_id: Query[Element, Any] = Query(
    'internal id', lambda element: element().id
)


def css_property(name: str) -> Query[Element, str]:
    def fn(element: Element) -> str:
        return element().value_of_css_property(name)

    return Query(f'css property {name}', fn)


def js_property(name: str) -> Query[Element, str]:
    def fn(element: Element) -> str:
        return element().get_property(name)

    return Query(f'js property {name}', fn)


url: Query[Browser, str] = Query(
    'url', lambda browser: browser.driver.current_url
)

title: Query[Browser, str] = Query(
    'title', lambda browser: browser.driver.title
)

tabs: Query[Browser, List[str]] = Query(
    'tabs', lambda browser: browser.driver.window_handles
)

tabs_number: Query[Browser, int] = Query(
    'tabs number', lambda browser: len(browser.driver.window_handles)
)


def tab(index: int) -> Query[Browser, str]:
    def fn(browser: Browser) -> str:
        return browser.driver.window_handles[index]

    return Query(f'tab by index {index}', fn)


current_tab: Query[Browser, str] = Query(
    'current tab (window handle)',
    lambda browser: browser.driver.current_window_handle,
)


def __next_tab_fn(browser: Browser) -> str:
    tabs = browser.driver.window_handles
    current = browser.driver.current_window_handle
    current_index = tabs.index(current)
    return (
        tabs[0] if current_index >= len(tabs) - 1 else tabs[current_index + 1]
    )


next_tab: Query[Browser, str] = Query('next tab', __next_tab_fn)


def __previous_tab_fn(browser: Browser) -> str:
    tabs = browser.driver.window_handles
    current = browser.driver.current_window_handle
    current_index = tabs.index(current)
    return tabs[-1] if current_index == 0 else tabs[current_index - 1]


previous_tab: Query[Browser, str] = Query('previous tab', __previous_tab_fn)

page_source: Query[Browser, str] = Query(
    'page source', lambda browser: browser.driver.page_source
)
