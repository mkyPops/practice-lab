"""
A fixed-capacity Least Recently Used (LRU) cache.

Implemented with collections.OrderedDict, which maintains insertion order
and allows O(1) reordering (move_to_end) and O(1) popping from either end.
Both get() and put() run in O(1) average time.
"""

from collections import OrderedDict
from typing import Any


class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._data: OrderedDict[Any, Any] = OrderedDict()

    def get(self, key: Any) -> Any:
        """Return the value for key, or None if not present.

        Accessing a key marks it as most recently used.
        """
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: Any, value: Any) -> None:
        """Insert or update a key/value pair, evicting the LRU item if full."""
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self.capacity:
            # popitem(last=False) removes the least recently used entry
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: Any) -> bool:
        return key in self._data


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, "a")
    cache.put(2, "b")
    print(cache.get(1))   # "a" -> 1 becomes most recently used
    cache.put(3, "c")     # evicts key 2 (least recently used)
    print(cache.get(2))   # None
    print(cache.get(3))   # "c"
