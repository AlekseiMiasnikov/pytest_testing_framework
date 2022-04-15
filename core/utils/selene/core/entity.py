from __future__ import annotations

import warnings
from abc import abstractmethod, ABC
from typing import TypeVar, Union, List, Dict, Any, Callable, Tuple

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.utils.selene.common.fp import pipe
from core.utils.selene.common.helpers import to_by, flatten, is_absolute_url
from core.utils.selene.core.condition import Condition, not_
from core.utils.selene.core.configuration import Config
from core.utils.selene.core.exceptions import TimeoutException, _SeleneError
from core.utils.selene.core.locator import Locator
from core.utils.selene.core.wait import Wait, Command, Query

E = TypeVar('E', bound='Assertable')
R = TypeVar('R')


class Assertable(ABC):
    @abstractmethod
    def should(self, condition: Condition[E]) -> E:
        pass


class Matchable(Assertable):
    @abstractmethod
    def wait_until(self, condition: Condition[E]) -> bool:
        pass

    @abstractmethod
    def matching(self, condition: Condition[E]) -> bool:
        pass


class Configured(ABC):
    @property
    @abstractmethod
    def config(self) -> Config:
        pass


class WaitingEntity(Matchable, Configured):
    def __init__(self, config: Config):
        self._config = config

    @property
    def wait(self) -> Wait[E]:
        return self.config.wait(self)

    def perform(self, command: Command[E]) -> E:
        self.wait.for_(command)
        return self

    def get(self, query: Query[E, R]) -> R:
        return self.wait.for_(query)

    @property
    def config(self) -> Config:
        return self._config

    def should(self, condition: Condition[E]) -> E:
        self.wait.for_(condition)
        return self

    def wait_until(self, condition: Condition[E]) -> bool:
        return self.wait.until(condition)

    def matching(self, condition: Condition[E]) -> bool:
        return condition.predicate(self)


class Element(WaitingEntity):
    @staticmethod
    def _log_webelement_outer_html_for(
            element: Element,
    ) -> Callable[[TimeoutException], Exception]:
        def log_webelement_outer_html(error: TimeoutException) -> Exception:
            from core.utils.selene.core import query
            from core.utils.selene.core.match import element_is_present

            cached = element.cached

            if cached.matching(element_is_present):
                return TimeoutException(
                    error.msg
                    + f'\nActual webelement: {query.outer_html(element)}'
                )
            else:
                return error

        return log_webelement_outer_html

    def __init__(self, locator: Locator[WebElement], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Config = None, **config_as_kwargs) -> Element:
        return Element(
            self._locator, self.config.with_(config, **config_as_kwargs)
        )

    def __str__(self):
        return str(self._locator)

    def __call__(self) -> WebElement:
        return self._locator()

    @property
    def wait(self) -> Wait[E]:
        if self.config.log_outer_html_on_failure:
            return super().wait.or_fail_with(
                pipe(
                    Element._log_webelement_outer_html_for(self),
                    super().wait.hook_failure,
                )
            )
        else:
            return super().wait

    @property
    def cached(self) -> Element:
        cache = None
        error = None
        try:
            cache = self()
        except Exception as e:
            error = e

        def get_webelement():
            if cache:
                return cache
            raise error

        return Element(
            Locator(f'{self}.cached', lambda: get_webelement()), self.config
        )

    def element(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})', lambda: self().find_element(*by)),
            self.config,
        )

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})', lambda: self().find_elements(*by)),
            self.config,
        )

    def execute_script(self, script_on_self: str, *extra_args):
        driver: WebDriver = self.config.driver
        webelement = self()
        return driver.execute_script(script_on_self, webelement, *extra_args)

    def _execute_script(
            self,
            script_on_self_element_and_args: str,
            *extra_args,
    ):
        driver: WebDriver = self.config.driver
        webelement = self()
        return driver.execute_script(
            f'''
                return (function(element, args) {{
                    {script_on_self_element_and_args}
                }})(arguments[0], arguments[1])
            ''',
            webelement,
            extra_args,
        )

    def set_value(self, value: Union[str, int]) -> Element:
        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.clear()
            webelement.send_keys(str(value))

        from core.utils.selene.core import command
        self.wait.for_(
            command.js.set_value(value)
            if self.config.set_value_by_js
            else Command(f'set value: {value}', fn)
        )
        return self

    def _actual_visible_webelement_and_maybe_its_cover(
            self, center_x_offset=0, center_y_offset=0
    ) -> Tuple[WebElement, WebElement]:
        results = self._execute_script(
            '''
                var centerXOffset = args[0];
                var centerYOffset = args[1];

                var isVisible = !!(
                    element.offsetWidth
                    || element.offsetHeight
                    || element.getClientRects().length
                ) && window.getComputedStyle(element).visibility !== 'hidden'

                if (!isVisible) {
                    throw `element ${element.outerHTML} is not visible`
                }

                var rect = element.getBoundingClientRect();
                var x = rect.left + rect.width/2 + centerXOffset;
                var y = rect.top + rect.height/2 + centerYOffset;

                var elementByXnY = document.elementFromPoint(x,y);
                if (elementByXnY == null) {
                    return [element, null];
                }

                var isNotOverlapped = element.isSameNode(elementByXnY);

                return isNotOverlapped
                       ? [element, null]
                       : [element, elementByXnY];
            ''',
            center_x_offset,
            center_y_offset,
        )
        webelement = results[0]
        maybe_cover = results[1]

        return webelement, maybe_cover

    @property
    def _actual_not_overlapped_webelement(self):
        (
            webelement,
            maybe_cover,
        ) = self._actual_visible_webelement_and_maybe_its_cover()
        if maybe_cover is not None:
            raise _SeleneError(
                lambda: f'Element: {webelement.get_attribute("outerHTML")}\n'
                        + '\tis overlapped by: '
                        + maybe_cover.get_attribute("outerHTML")
            )

        return webelement

    def type(self, text: Union[str, int]) -> Element:
        def fn(element: Element):
            if self.config.wait_for_no_overlap_found_by_js:
                webelement = element._actual_not_overlapped_webelement
            else:
                webelement = element()
            webelement.send_keys(str(text))

        from core.utils.selene.core import command

        self.wait.for_(
            command.js.type(text)
            if self.config.type_by_js
            else Command(f'type: {text}', fn)
        )

        return self

    def press(self, *keys) -> Element:
        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.send_keys(*keys)

        self.wait.command(f'press keys: {keys}', fn)

        return self

    def press_enter(self) -> Element:
        return self.press(Keys.ENTER)

    def press_escape(self) -> Element:
        return self.press(Keys.ESCAPE)

    def press_tab(self) -> Element:
        return self.press(Keys.TAB)

    def clear(self) -> Element:
        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.clear()

        self.wait.command('clear', fn)

        return self

    def submit(self) -> Element:
        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.submit()

        self.wait.command('submit', fn)

        return self

    def click(self) -> Element:
        self.wait.command('click', lambda element: element().click_by_id())
        return self

    def double_click(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            actions.double_click(webelement).perform()

        self.wait.command('double click', fn)

        return self

    def context_click(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            actions.context_click(webelement).perform()

        self.wait.command('context click', fn)

        return self

    def hover(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            actions.move_to_element(webelement).perform()

        self.wait.command('hover', fn)

        return self

    def should(
            self, condition: Condition[[], Element], timeout: int = None
    ) -> Element:
        if timeout:
            warnings.warn(
                "using timeout argument is deprecated; "
                "use `browser.element('#foo').with_(Config(timeout=6)).should(be.enabled)`"
                "or just `...with_(timeout=6).should(...` style instead",
                DeprecationWarning,
            )
            return self.with_(Config(timeout=timeout)).should(condition)

        super().should(condition)
        return self

    # --- Deprecated --- #

    def get_actual_webelement(self) -> WebElement:
        warnings.warn(
            "considering to be deprecated; use element as callable instead, like: browser.element('#foo')()",
            PendingDeprecationWarning,
        )
        return self()

    def caching(self) -> Element:
        warnings.warn(
            "deprecated; use `cached` property instead: browser.element('#foo').cached",
            DeprecationWarning,
        )
        return self.cached

    def s(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        return self.element(css_or_xpath_or_by)

    def find(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        warnings.warn(
            "deprecated; consider using `element` instead: browser.element('#foo').element('.bar')",
            DeprecationWarning,
        )
        return self.element(css_or_xpath_or_by)

    def ss(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        return self.all(css_or_xpath_or_by)

    def find_all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; consider using `all` instead: browser.element('#foo').all('.bar')",
            DeprecationWarning,
        )
        return self.all(css_or_xpath_or_by)

    def elements(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; consider using `all` instead: browser.element('#foo').all('.bar')",
            DeprecationWarning,
        )
        return self.all(css_or_xpath_or_by)

    @property
    def parent_element(self):
        warnings.warn(
            "considering to deprecate because such impl makes less sens for mobile automation; "
            "consider using corresponding xpath instead if you really need it for web:"
            "browser.element('#foo').element('..')",
            PendingDeprecationWarning,
        )
        return self.element('..')

    @property
    def following_sibling(self):
        warnings.warn(
            "considering to deprecate because such impl makes less sens for mobile automation; "
            "consider using corresponding xpath instead if you really need it for web:"
            "browser.element('#foo').element('./following-sibling::*')",
            PendingDeprecationWarning,
        )
        return self.element('./following-sibling::*')

    @property
    def first_child(self):
        warnings.warn(
            "considering to deprecate because such impl makes less sens for mobile automation; "
            "consider using corresponding xpath instead if you really need it for web: "
            "browser.element('#foo').element('./*[1]')",
            PendingDeprecationWarning,
        )
        return self.element('./*[1]')

    def assure(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method instead: browser.element('#foo').should(be.enabled)",
            DeprecationWarning,
        )
        return self.should(condition, timeout)

    def should_be(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.*` style conditions instead: "
            "browser.element('#foo').should(be.enabled)",
            DeprecationWarning,
        )
        return self.should(condition, timeout)

    def should_have(
            self, condition: ElementCondition, timeout=None
    ) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `have.*` style conditions instead: "
            "browser.element('#foo').should(have.text('bar')",
            DeprecationWarning,
        )
        return self.should(condition, timeout)

    def should_not(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not_.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)

    def assure_not(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not_.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)

    def should_not_be(
            self, condition: ElementCondition, timeout=None
    ) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not_.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)

    def should_not_have(
            self, condition: ElementCondition, timeout=None
    ) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not_.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)

    def set(self, value: Union[str, int]) -> Element:
        warnings.warn(
            "deprecated; use `set_value` method instead", DeprecationWarning
        )
        return self.set_value(value)

    def scroll_to(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').perform(command.js.scroll_into_view)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import command

        self.perform(command.js.scroll_into_view)
        return self

    def press_down(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').type(Keys.ARROW_DOWN)` style instead",
            DeprecationWarning,
        )
        return self.type(Keys.ARROW_DOWN)

    def find_element(self, by=By.ID, value=None):
        warnings.warn(
            "deprecated; use `browser.element('#foo').should(be.in_dom)().find_element(by, value)` style instead",
            DeprecationWarning,
        )
        self.wait.command(
            'find element', lambda element: element().find_element(by, value)
        )
        return self

    def find_elements(self, by=By.ID, value=None):
        warnings.warn(
            "deprecated; use `browser.element('#foo').should(be.in_dom)().find_elements(by, value)` style instead",
            DeprecationWarning,
        )
        self.wait.command(
            'find elements', lambda element: element().find_elements(by, value)
        )
        return self

    def send_keys(self, *value) -> Element:
        self.wait.command(
            'send keys', lambda element: element().send_keys(*value)
        )
        return self

    @property
    def tag_name(self) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.tag_name)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.tag)

    @property
    def text(self) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.text)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.text)

    def attribute(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.attribute('name'))` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.attribute(name))

    def js_property(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.js_property('name'))` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.js_property(name))

    def value_of_css_property(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.css_property('name'))` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.css_property(name))

    def get_attribute(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.attribute('name'))` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.attribute(name))

    def get_property(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.js_property('name'))` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.js_property(name))

    def is_selected(self) -> bool:
        warnings.warn(
            "deprecated; use `browser.element('#foo').matching(be.selected)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.support.conditions import be

        return self.matching(be.selected)

    def is_enabled(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').matching(be.enabled)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.support.conditions import be

        return self.matching(be.enabled)

    def is_displayed(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').matching(be.visible)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.support.conditions import be

        return self.matching(be.visible)

    @property
    def location(self) -> Dict[str, int]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.location)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.location)

    @property
    def location_once_scrolled_into_view(self) -> Dict[str, int]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.location_once_scrolled_into_view)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.location_once_scrolled_into_view)

    @property
    def size(self) -> Dict[str, Any]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.size)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.size)

    @property
    def rect(self) -> Dict[str, Any]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.rect)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.rect)

    @property
    def screenshot_as_base64(self) -> Any:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.screenshot_as_base64)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.screenshot_as_base64)

    @property
    def screenshot_as_png(self) -> Any:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.screenshot_as_base64)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.screenshot_as_png)

    def screenshot(self, filename: str) -> bool:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.screenshot('filename'))` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.screenshot(filename))

    @property
    def parent(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo')().parent` style for the majority of cases",
            DeprecationWarning,
        )
        return self.get(
            Query('parent search context', lambda element: element().parent)
        )

    @property
    def id(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.internal_id)` style instead",
            DeprecationWarning,
        )
        from core.utils.selene.core import query

        return self.get(query.internal_id)


class SeleneElement(Element):
    pass


class Collection(WaitingEntity):
    def __init__(self, locator: Locator[List[WebElement]], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Config = None, **config_as_kwargs) -> Collection:
        return Collection(
            self._locator, self.config.with_(config, **config_as_kwargs)
        )

    def __str__(self):
        return str(self._locator)

    def __call__(self) -> List[WebElement]:
        return self._locator()

    @property
    def cached(self) -> Collection:
        webelements = self()
        return Collection(
            Locator(f'{self}.cached', lambda: webelements), self.config
        )

    def __iter__(self):
        i = 0
        cached = self.cached
        while i < len(cached()):
            element = cached[i]
            yield element
            i += 1

    def __len__(self):
        from core.utils.selene.core import query

        return self.get(query.size)

    def element(self, index: int) -> Element:
        def find() -> WebElement:
            webelements = self()
            length = len(webelements)

            if length <= index:
                raise AssertionError(
                    f'Cannot get element with index {index} '
                    + f'from webelements collection with length {length}'
                )

            return webelements[index]

        return Element(Locator(f'{self}[{index}]', find), self.config)

    @property
    def first(self):
        return self.element(0)

    def sliced(self, start: int, stop: int, step: int = 1) -> Collection:
        def find() -> List[WebElement]:
            webelements = self()
            return webelements[start:stop:step]

        return Collection(
            Locator(f'{self}[{start}:{stop}:{step}]', find), self.config
        )

    def __getitem__(
            self, index_or_slice: Union[int, slice]
    ) -> Union[Element, Collection]:
        if isinstance(index_or_slice, slice):
            return self.sliced(
                index_or_slice.start, index_or_slice.stop, index_or_slice.step
            )

        return self.element(index_or_slice)

    def from_(self, start: int) -> Collection:
        return self[start:]

    def to(self, stop: int) -> Collection:
        return self[:stop]

    def filtered_by(
            self, condition: Union[Condition[[], Element], Callable[[E], None]]
    ) -> Collection:
        condition = (
            condition
            if isinstance(condition, Condition)
            else Condition(str(condition), condition)
        )

        return Collection(
            Locator(
                f'{self}.filtered_by({condition})',
                lambda: [
                    element()
                    for element in self.cached
                    if element.matching(condition)
                ],
            ),
            self.config,
        )

    def filtered_by_their(
            self,
            selector_or_callable: Union[str, tuple, Callable[[Element], Element]],
            condition: Condition[[], Element],
    ) -> Collection:
        warnings.warn(
            'filtered_by_their is experimental; might be renamed or removed in future',
            FutureWarning,
        )

        def find_in(parent: Element):
            if callable(selector_or_callable):
                return selector_or_callable(parent)
            else:
                return parent.element(selector_or_callable)

        return self.filtered_by(lambda it: condition(find_in(it)))

    def element_by(
            self, condition: Union[Condition[[], Element], Callable[[E], None]]
    ) -> Element:
        condition = (
            condition
            if isinstance(condition, Condition)
            else Condition(str(condition), condition)
        )

        def find() -> WebElement:
            cached = self.cached

            for element in cached:
                if element.matching(condition):
                    return element()

            from core.utils.selene.core import query

            if self.config.log_outer_html_on_failure:
                outer_htmls = [query.outer_html(element) for element in cached]

                raise AssertionError(
                    f'\n\tCannot find element by condition «{condition}» '
                    f'\n\tAmong {self}'
                    f'\n\tActual webelements collection:'
                    f'\n\t{outer_htmls}'
                )
            else:
                raise AssertionError(
                    f'\n\tCannot find element by condition «{condition}» '
                    f'\n\tAmong {self}'
                )

        return Element(
            Locator(f'{self}.element_by({condition})', find), self.config
        )

    def element_by_its(
            self,
            selector_or_callable: Union[str, tuple, Callable[[Element], Element]],
            condition: Condition[[], Element],
    ) -> Element:
        warnings.warn(
            'element_by_its is experimental; might be renamed or removed in future',
            FutureWarning,
        )

        def find_in(parent: Element):
            if callable(selector_or_callable):
                return selector_or_callable(parent)
            else:
                return parent.element(selector_or_callable)

        return self.element_by(lambda it: condition(find_in(it)))

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            'might be renamed or deprecated in future; '
            'all is actually a shortcut for collected(lambda element: element.all(selector)...'
            'but we also have all_first and...'
            'it is yet unclear what name would be best for all_first as addition to all... '
            'all_first might confuse with all(...).first... I mean: '
            'all_first(selector) is actually '
            'collected(lambda e: e.element(selector)) '
            'but it is not the same as '
            'all(selector).first '
            'that is collected(lambda e: e.all(selector)).first ... o_O ',
            FutureWarning,
        )
        by = to_by(css_or_xpath_or_by)
        return Collection(
            Locator(
                f'{self}.all({by})',
                lambda: flatten(
                    [webelement.find_elements(*by) for webelement in self()]
                ),
            ),
            self.config,
        )

    def all_first(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            'might be renamed or deprecated in future; '
            'it is yet unclear what name would be best... '
            'all_first might confuse with all(...).first... I mean: '
            'all_first(selector) is actually '
            'collected(lambda e: e.element(selector)) '
            'but it is not the same as '
            'all(selector).first '
            'that is collected(lambda e: e.all(selector)).first ... o_O ',
            FutureWarning,
        )
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(
                f'{self}.all_first({by})',
                lambda: [
                    webelement.find_element(*by) for webelement in self()
                ],
            ),
            self.config,
        )

    def collected(
            self, finder: Callable[[Element], Union[Element, Collection]]
    ) -> Collection:
        return Collection(
            Locator(
                f'{self}.collected({finder})',
                lambda: flatten(
                    [finder(element)() for element in self.cached]
                ),
            ),
            self.config,
        )

    def should(
            self,
            condition: Union[Condition[[], Collection], Condition[[], Element]],
            timeout: int = None,
    ) -> Collection:
        if isinstance(condition, ElementCondition):
            for element in self:
                if timeout:
                    warnings.warn(
                        "using timeout argument is deprecated; "
                        "use `browser.all('.foo').with_(Config(timeout=6)).should(have.size(0))`"
                        "or just `...with_(timeout=6).should(...` style instead",
                        DeprecationWarning,
                    )
                    element.with_(Config(timeout=timeout)).should(condition)
                element.should(condition)
        else:
            if timeout:
                warnings.warn(
                    "using timeout argument is deprecated; "
                    "use `browser.all('.foo').with_(Config(timeout=6)).should(have.size(0))` "
                    "or just `...with_(timeout=6).should(...` style instead",
                    DeprecationWarning,
                )
                self.with_(Config(timeout=timeout)).should(condition)
            super().should(condition)
        return self

    def get_actual_webelements(self) -> List[WebElement]:
        warnings.warn(
            "considering to be deprecated; use collection as callable instead, like: browser.all('.foo')()",
            PendingDeprecationWarning,
        )
        return self()

    def caching(self) -> Collection:
        warnings.warn(
            "deprecated; use `cached` property instead: browser.all('#foo').cached",
            DeprecationWarning,
        )
        return self.cached

    def all_by(self, condition: Condition[[], Element]) -> Collection:
        warnings.warn(
            "deprecated; use `filtered_by` instead: browser.all('.foo').filtered_by(be.enabled)",
            DeprecationWarning,
        )
        return self.filtered_by(condition)

    def filter_by(self, condition: Condition[[], Element]) -> Collection:
        warnings.warn(
            "deprecated; use `filtered_by` instead: browser.all('.foo').filtered_by(be.enabled)",
            DeprecationWarning,
        )
        return self.filtered_by(condition)

    def find_by(self, condition: Condition[[], Element]) -> Element:
        warnings.warn(
            "deprecated; use `element_by` instead: browser.all('.foo').element_by(be.enabled)",
            DeprecationWarning,
        )
        return self.element_by(condition)

    def size(self):
        warnings.warn(
            "deprecated; use `len` standard function instead: len(browser.all('.foo'))",
            DeprecationWarning,
        )
        return len(self)

    def should_each(
            self, condition: ElementCondition, timeout=None
    ) -> Collection:
        return self.should(condition, timeout)

    def assure(
            self,
            condition: Union[CollectionCondition, ElementCondition],
            timeout=None,
    ) -> Collection:
        warnings.warn(
            "deprecated; use `should` method instead: browser.all('.foo').should(have.size(0))",
            DeprecationWarning,
        )
        return self.should(condition, timeout)

    def should_be(
            self,
            condition: Union[CollectionCondition, ElementCondition],
            timeout=None,
    ) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.*` style conditions instead: "
            "browser.all('.foo').should(be.*)",
            DeprecationWarning,
        )
        return self.should(condition, timeout)

    def should_have(
            self,
            condition: Union[CollectionCondition, ElementCondition],
            timeout=None,
    ) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `have.*` style conditions instead: "
            "browser.all('.foo').should(have.size(0))",
            DeprecationWarning,
        )
        return self.should(condition, timeout)

    def should_not(
            self,
            condition: Union[CollectionCondition, ElementCondition],
            timeout=None,
    ) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.all('.foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)

    def assure_not(
            self,
            condition: Union[CollectionCondition, ElementCondition],
            timeout=None,
    ) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.all('.foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)

    def should_not_be(
            self,
            condition: Union[CollectionCondition, ElementCondition],
            timeout=None,
    ) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.all('.foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)

    def should_not_have(
            self,
            condition: Union[CollectionCondition, ElementCondition],
            timeout=None,
    ) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not_.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning,
        )
        return self.should(not_(condition), timeout)


class SeleneCollection(Collection):
    pass


class Browser(WaitingEntity):
    def __init__(
            self, config: Config
    ):
        super().__init__(config)

    def with_(self, config: Config = None, **config_as_kwargs) -> Browser:
        return Browser(self.config.with_(config, **config_as_kwargs))

    def __str__(self):
        return 'browser'

    @property
    def driver(self) -> WebDriver:
        return self.config.driver

    def element(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(
                f'{self}.element({by})', lambda: self.driver.find_element(*by)
            ),
            self.config,
        )

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(
                f'{self}.all({by})', lambda: self.driver.find_elements(*by)
            ),
            self.config,
        )

    def open(self, relative_or_absolute_url: str) -> Browser:
        width = self.config.window_width
        height = self.config.window_height

        if width and height:
            self.driver.set_window_size(int(width), int(height))

        is_absolute = is_absolute_url(relative_or_absolute_url)
        base_url = self.config.base_url
        url = (
            relative_or_absolute_url
            if is_absolute
            else base_url + relative_or_absolute_url
        )

        self.driver.get(url)
        return self

    def switch_to_next_tab(self) -> Browser:
        from core.utils.selene.core import query

        self.driver.switch_to.window(query.next_tab(self))

        return self

    def switch_to_previous_tab(self) -> Browser:
        from core.utils.selene.core import query

        self.driver.switch_to.window(query.previous_tab(self))
        return self

    def switch_to_tab(self, index_or_name: Union[int, str]) -> Browser:
        if isinstance(index_or_name, int):
            index = index_or_name
            from core.utils.selene.core import query

            self.driver.switch_to.window(query.tab(index)(self))
        else:
            self.driver.switch_to.window(index_or_name)

        return self

    @property
    def switch_to(self) -> SwitchTo:
        return self.driver.switch_to

    def close_current_tab(self) -> Browser:
        self.driver.close()
        return self

    def quit(self) -> None:
        self.driver.quit()

    def clear_local_storage(self) -> Browser:
        self.driver.execute_script(
            'window.localStorage.clear();'
        )
        return self

    def clear_session_storage(self) -> Browser:
        self.driver.execute_script('window.sessionStorage.clear();')
        return self

    def should(self, condition: BrowserCondition) -> Browser:
        super().should(condition)
        return self

    def close(self) -> Browser:
        warnings.warn(
            "deprecated; use a `close_current_tab` method instead",
            DeprecationWarning,
        )

        return self.close_current_tab()

    def quit_driver(self) -> None:
        warnings.warn(
            "deprecated; use a `quit` method instead", DeprecationWarning
        )
        self.quit()

    @classmethod
    def wrap(cls, webdriver: WebDriver):
        warnings.warn(
            "deprecated; use a normal constructor style instead: "
            "`Browser(Config(driver=webdriver))`",
            DeprecationWarning,
        )
        return Browser(Config(driver=webdriver))

    def s(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        warnings.warn(
            "deprecated; use an `element` method instead: "
            "`browser.element('#foo')`",
            DeprecationWarning,
        )

        return self.element(css_or_xpath_or_by)

    def find(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        warnings.warn(
            "deprecated; use an `element` method instead: "
            "`browser.element('#foo')`",
            DeprecationWarning,
        )

        return self.element(css_or_xpath_or_by)

    def ss(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; use an `all` method instead: "
            "`browser.all('.foo')`",
            DeprecationWarning,
        )

        return self.all(css_or_xpath_or_by)

    def find_all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; use an `all` method instead: "
            "`browser.all('.foo')`",
            DeprecationWarning,
        )

        return self.all(css_or_xpath_or_by)

    def elements(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; use an `all` method instead: "
            "`browser.all('.foo')`",
            DeprecationWarning,
        )

        return self.all(css_or_xpath_or_by)

    def find_elements(self, by=By.ID, value=None):
        warnings.warn(
            "deprecated; use instead: `browser.driver.find_elements(...)`",
            DeprecationWarning,
        )
        return self.driver.find_elements(by, value)

    def find_element(self, by=By.ID, value=None):
        warnings.warn(
            "deprecated; use instead: `browser.driver.find_element(...)`",
            DeprecationWarning,
        )
        return self.driver.find_element(by, value)


from core.utils.selene.core.conditions import (
    CollectionCondition,
    ElementCondition,
    BrowserCondition,
)


class SeleneDriver(Browser):
    pass
