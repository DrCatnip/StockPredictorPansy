import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from backend.app.core.cache import TTLCache


class TTLCacheTests(unittest.TestCase):
    def test_concurrent_requests_share_one_producer(self):
        cache = TTLCache()
        worker_count = 8
        start = threading.Barrier(worker_count)
        counter_lock = threading.Lock()
        calls = 0

        def producer():
            nonlocal calls
            with counter_lock:
                calls += 1
            time.sleep(0.03)
            return "model-bundle"

        def request_value(_):
            start.wait()
            return cache.get_or_set("same-key", 60, producer)

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            results = list(executor.map(request_value, range(worker_count)))

        self.assertEqual(results, ["model-bundle"] * worker_count)
        self.assertEqual(calls, 1)

    def test_expired_value_is_recomputed(self):
        cache = TTLCache()
        self.assertEqual(cache.get_or_set("key", 0, lambda: 1), 1)
        self.assertEqual(cache.get_or_set("key", 60, lambda: 2), 2)


if __name__ == "__main__":
    unittest.main()