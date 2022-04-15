from core.utils.selene.core import match
from core.utils.selene.support.conditions import not_ as _not_

not_ = _not_

visible = match.element_is_visible
hidden = match.element_is_hidden
selected = match.element_is_selected

present = match.element_is_present
in_dom = match.element_is_present
existing = match.element_is_present

absent = match.element_is_absent

enabled = match.element_is_enabled
disabled = match.element_is_disabled

clickable = match.element_is_clickable

blank = match.element_is_blank

empty = match.collection_is_empty
