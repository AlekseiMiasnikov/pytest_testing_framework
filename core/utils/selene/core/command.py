from typing import Union

from core.utils.selene.core.entity import Element
from core.utils.selene.core.wait import Command


class js:
    @staticmethod
    def set_value(value: Union[str, int]) -> Command[Element]:
        def fn(element: Element):
            element.execute_script(
                """return (function(element, text) {
                    var maxlength = element.getAttribute('maxlength') === null
                        ? -1
                        : parseInt(element.getAttribute('maxlength'));
                    element.value = maxlength === -1
                        ? text
                        : text.length <= maxlength
                            ? text
                            : text.substring(0, maxlength);
                    return null;
                })(arguments[0], arguments[1]);""",
                str(value),
            )

        return Command(f'set value by js: {value}', fn)

    @staticmethod
    def type(keys: Union[str, int]) -> Command[Element]:
        def fn(element: Element):
            element.execute_script(
                """return (function(element, textToAppend) {
                    var value = element.value || '';
                    var text = value + textToAppend;
                    var maxlength = element.getAttribute('maxlength') === null
                        ? -1
                        : parseInt(element.getAttribute('maxlength'));
                    element.value = maxlength === -1
                        ? text
                        : text.length <= maxlength
                            ? text
                            : text.substring(0, maxlength);
                    return null;
                })(arguments[0], arguments[1]);""",
                str(keys),
            )

        return Command(f'set value by js: {keys}', fn)

    scroll_into_view = Command(
        'scroll into view',
        lambda element: element.execute_script(
            """return (function(element) {
                element.scrollIntoView(true);
            })(arguments[0]);"""
        ),
    )

    click = Command(
        'click',
        lambda element: element.execute_script(
            """return (function(element) {
                element.click();
            })(arguments[0]);"""
        ),
    )
