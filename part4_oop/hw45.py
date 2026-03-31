from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class BaseQueuePolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    @property
    def has_keys(self) -> bool:
        return bool(self._order)

    def get_key_to_evict(self) -> K | None:
        if self._needs_eviction:
            return None

        return self._order[0]

    def remove_key(self, key: K) -> None:
        if key not in self._order:
            return

        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def _needs_eviction(self) -> bool:
        return not self.has_keys or len(self._order) < self.capacity


class FIFOPolicy(BaseQueuePolicy[K]):
    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)


class LRUPolicy(BaseQueuePolicy[K]):
    def register_access(self, key: K) -> None:
        self.remove_key(key)
        self._order.append(key)


@dataclass
class BaseDictPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    @property
    def has_keys(self) -> bool:
        return bool(self._key_counter)

    def register_access(self, key: K) -> None: ...

    def get_key_to_evict(self) -> K | None: ...

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def _needs_eviction(self) -> bool:
        return not self.has_keys or len(self._key_counter) < self.capacity


class LFUPolicy(BaseDictPolicy[K]):
    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_counter[key] = 0

        self._key_counter[key] += 1

    def get_key_to_evict(self) -> K | None:
        if self._needs_eviction:
            return None

        last_added_element = next(reversed(self._key_counter))

        ans_key: K | None = None
        for cur_key in self._key_counter:
            if cur_key == last_added_element:
                continue

            if ans_key is None or self._key_counter[ans_key] > self._key_counter[cur_key]:
                ans_key = cur_key

        return ans_key


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.policy.register_access(key)
        self.storage.set(key, value)

        key_to_evict = self.policy.get_key_to_evict()
        if key_to_evict:
            self.storage.remove(key_to_evict)
            self.policy.remove_key(key_to_evict)

    def get(self, key: K) -> V | None:
        self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        
