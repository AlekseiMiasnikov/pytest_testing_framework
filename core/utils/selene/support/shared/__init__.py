from __future__ import annotations

from core.utils.selene.support.shared.browser import SharedBrowser
from core.utils.selene.support.shared.config import SharedConfig

config = SharedConfig()

browser = SharedBrowser(config)
