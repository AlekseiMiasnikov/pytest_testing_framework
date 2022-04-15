from core.utils.selene.core.condition import Condition
from core.utils.selene.core.entity import Browser, Element, Collection


class ElementCondition(Condition[[], Element]):
    pass


class CollectionCondition(Condition[[], Collection]):
    pass


BrowserCondition = Condition[[], Browser]
