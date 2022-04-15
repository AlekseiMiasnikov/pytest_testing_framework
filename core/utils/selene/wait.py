import warnings

from core.utils.selene.core.wait import Wait


def wait_for(entity, condition, timeout=4, polling=0.1):
    warnings.warn(
        'deprecated, use Wait(entity, at_most=timeout).for_(condition)',
        DeprecationWarning,
    )
    return Wait(entity, at_most=timeout).for_(condition)
