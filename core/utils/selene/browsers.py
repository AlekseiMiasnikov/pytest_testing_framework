import warnings


class _ClassPropertyDescriptor:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def _classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return _ClassPropertyDescriptor(func)


class BrowserName:
    @_classproperty
    def CHROME(self):
        warnings.warn(
            "might be deprecated, consider using 'chrome' explicitly",
            PendingDeprecationWarning,
        )
        return 'chrome'

    @_classproperty
    def FIREFOX(self):
        warnings.warn(
            "might be deprecated, consider using 'firefox' explicitly",
            PendingDeprecationWarning,
        )
        return 'firefox'

    @_classproperty
    def MARIONETTE(self):
        warnings.warn(
            "might be deprecated, consider using 'firefox' explicitly",
            PendingDeprecationWarning,
        )
        return 'firefox'

    @_classproperty
    def PHANTOMJS(self):
        warnings.warn(
            "might be deprecated, consider using 'phantomjs' explicitly",
            PendingDeprecationWarning,
        )
        return 'chrome'
