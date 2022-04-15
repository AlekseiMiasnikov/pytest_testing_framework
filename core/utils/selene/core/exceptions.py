from typing import Union, Callable


class TimeoutException(AssertionError):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        exception_msg = "Message: %s\n" % self.msg
        return exception_msg


class ConditionNotMatchedError(AssertionError):
    def __init__(self, message='condition not matched'):
        super().__init__(message)


class _SeleneError(AssertionError):
    def __init__(self, message: Union[str, Callable[[], str]]):
        self._render_message: Callable[[], str] = (
            (lambda: message) if isinstance(message, str) else message
        )

    @property
    def args(self):
        return (self._render_message(),)

    def __str__(self):
        return self._render_message()

    def __repr__(self):
        return f"SeleneError: {self._render_message()}"
