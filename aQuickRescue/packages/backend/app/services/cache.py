import time
from threading import Lock
from typing import Any, Optional

class SimpleCache:
    """A tiny thread-safe in-memory TTL cache for local development/testing.

    Note: Not suitable for production (use Redis)."""

    def __init__(self):
        self._store = {}  # key -> (expiry_ts, value)
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            expiry, value = item
            if expiry < time.time():
                # expired
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: int):
        expiry = time.time() + ttl_seconds
        with self._lock:
            self._store[key] = (expiry, value)

    def invalidate(self, key: str):
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self):
        with self._lock:
            self._store.clear()

# Single global cache instance
cache = SimpleCache()

