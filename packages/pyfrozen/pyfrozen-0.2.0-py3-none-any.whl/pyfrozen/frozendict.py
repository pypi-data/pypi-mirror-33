from collections import Mapping, MutableMapping
from typing import Optional

__all__ = ("FrozenDict",)


class FrozenDict(MutableMapping):
    __slots__ = "_frozen", "_items"

    def __init__(self, *, items: Optional[dict] = None) -> None:
        self._frozen = False
        self._items = items or {}

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        self.assert_frozen()
        self._items[key] = value

    def __delitem__(self, key):
        self.assert_frozen()
        del self._items[key]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __repr__(self):
        return f"<FrozenDict(frozen={self._frozen}, {self._items!r})>"

    @property
    def frozen(self) -> bool:
        return self._frozen

    def assert_frozen(self) -> None:
        if self._frozen:
            raise RuntimeError("Cannot modify frozen dict")

    def freeze(self) -> None:
        self._frozen = True

    def update(self, *args, **kwargs) -> None:
        self.assert_frozen()

        if not args:
            raise TypeError(
                "Descriptor `update` of `FrozenDict` object needs an argument"
            )

        if len(args) > 1:
            raise TypeError(f"Update expected at most 1 arguments, got {len(args)}")

        arg = args[0]
        if isinstance(arg, Mapping):
            for key in arg:
                self._items[key] = arg[key]
        else:
            for key, value in arg:
                self._items[key] = value

        for key, value in kwargs.items():
            self._items[key] = value
