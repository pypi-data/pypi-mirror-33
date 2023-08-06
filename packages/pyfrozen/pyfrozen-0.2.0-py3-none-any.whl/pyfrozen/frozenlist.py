from collections import MutableSequence
from functools import total_ordering
from typing import Any, Optional

__all__ = ("FrozenList",)


@total_ordering
class FrozenList(MutableSequence):
    __slots__ = "_frozen", "_items"

    def __init__(self, *, items: Optional[list] = None) -> None:
        self._frozen = False
        self._items = items or []

    def __getitem__(self, index):
        return self._items[index]

    def __setitem__(self, index, value):
        self.assert_frozen()
        self._items[index] = value

    def __delitem__(self, index):
        self.assert_frozen()
        del self._items[index]

    def __len__(self):
        return self._items.__len__()

    def __iter__(self):
        return self._items.__iter__()

    def __reversed__(self):
        return self._items.__reversed__()

    def __eq__(self, other):
        return list(self) == other

    def __le__(self, other):
        return list(self) <= other

    def __repr__(self):
        return f"<FrozenList(frozen={self._frozen}, {self._items!r})>"

    @property
    def frozen(self) -> bool:
        return self._frozen

    def assert_frozen(self) -> None:
        if self._frozen:
            raise RuntimeError("Cannot modify frozen list")

    def freeze(self) -> None:
        self._frozen = True

    def insert(self, pos: int, item: Any) -> None:
        self.assert_frozen()
        self._items.insert(pos, item)
