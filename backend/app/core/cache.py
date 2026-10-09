from __future__ import annotations

import threading
import time
from typing import Any, Callable, Hashable


class TTLCache:
    """Small process-local cache for a single API worker."""

    def __init__(self) -> None:
        self._store: dict[Hashable, tuple[float, Any]] = {}
        self._inflight: dict[Hashable, threading.Event] = {}
        self._lock = threading.Lock()

    def get_or_set(self, key: Hashable, ttl: float, producer: Callable[[], Any]) -> Any:
        while True:
            with self._lock:
                cached = self._store.get(key)
                if cached is not None and time.monotonic() < cached[0]:
                    return cached[1]

                event = self._inflight.get(key)
                is_producer = event is None
                if is_producer:
                    event = threading.Event()
                    self._inflight[key] = event

            if not is_producer:
                event.wait()
                continue

            try:
                value = producer()
            except BaseException:
                with self._lock:
                    self._inflight.pop(key, None)
                event.set()
                raise

            with self._lock:
                self._store[key] = (time.monotonic() + ttl, value)
                self._inflight.pop(key, None)
            event.set()
            return value

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


history_cache = TTLCache()
info_cache = TTLCache()
market_cache = TTLCache()
model_cache = TTLCache()