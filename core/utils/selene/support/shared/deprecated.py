import warnings

from core.utils.selene.support.shared import config


class OldConfig:
    @property
    def timeout(self):
        warnings.warn(
            'selene.config.timeout is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.timeout

    @timeout.setter
    def timeout(self, value):
        warnings.warn(
            'selene.config.timeout is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.timeout = value

    @property
    def poll_during_waits(self):
        warnings.warn(
            'selene.config.poll_during_waits is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.poll_during_waits

    @poll_during_waits.setter
    def poll_during_waits(self, value):
        warnings.warn(
            'selene.config.poll_during_waits is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.poll_during_waits = value

    @property
    def base_url(self):
        warnings.warn(
            'selene.config.base_url is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.base_url

    @base_url.setter
    def base_url(self, value):
        warnings.warn(
            'selene.config.base_url is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.base_url = value

    @property
    def app_host(self):
        warnings.warn(
            'selene.config.app_host is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.base_url

    @app_host.setter
    def app_host(self, value):
        warnings.warn(
            'selene.config.app_host is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.base_url = value

    @property
    def cash_elements(self):
        warnings.warn(
            'selene.config.cash_elements is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.cash_elements

    @cash_elements.setter
    def cash_elements(self, value):
        warnings.warn(
            'selene.config.cash_elements is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.cash_elements = value

    @property
    def browser_name(self):
        warnings.warn(
            'selene.config.browser_name is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.browser_name

    @browser_name.setter
    def browser_name(self, value):
        warnings.warn(
            'selene.config.browser_name is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.browser_name = value

    @property
    def start_maximized(self):
        warnings.warn(
            'selene.config.start_maximized is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.start_maximized

    @start_maximized.setter
    def start_maximized(self, value):
        warnings.warn(
            'selene.config.start_maximized is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.start_maximized = value

    @property
    def hold_browser_open(self):
        warnings.warn(
            'selene.config.hold_browser_open is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.hold_browser_open

    @hold_browser_open.setter
    def hold_browser_open(self, value):
        warnings.warn(
            'selene.config.hold_browser_open is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.hold_browser_open = value

    @property
    def counter(self):
        warnings.warn(
            'selene.config.counter is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.counter

    @counter.setter
    def counter(self, value):
        warnings.warn(
            'selene.config.counter is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.counter = value

    @property
    def reports_folder(self):
        warnings.warn(
            'selene.config.reports_folder is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.reports_folder

    @reports_folder.setter
    def reports_folder(self, value):
        warnings.warn(
            'selene.config.reports_folder is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.reports_folder = value

    @property
    def desired_capabilities(self):
        warnings.warn(
            'selene.config.desired_capabilities is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        return config.desired_capabilities

    @desired_capabilities.setter
    def desired_capabilities(self, value):
        warnings.warn(
            'selene.config.desired_capabilities is deprecated, '
            'use `from selene.support.shared import config` import',
            DeprecationWarning,
        )
        config.desired_capabilities = value
