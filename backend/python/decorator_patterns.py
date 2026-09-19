"""
Practical decorator patterns: retry, timer, rate_limit, and singleton.
Each decorator is generic (works with any callable) and includes a
small real-world usage example demonstrating typical application.
"""

import time
import functools
import threading


def retry(times=3, delay=1.0, exceptions=(Exception,)):
    """Retry a function call on failure, with fixed delay between attempts."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < times:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


def timer(func):
    """Log the execution time of a function call."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def rate_limit(calls, period=1.0):
    """Limit a function to `calls` invocations per `period` seconds (thread-safe)."""
    def decorator(func):
        lock = threading.Lock()
        timestamps = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.monotonic()
                # drop timestamps outside the sliding window
                while timestamps and now - timestamps[0] > period:
                    timestamps.pop(0)
                if len(timestamps) >= calls:
                    wait_time = period - (now - timestamps[0])
                    time.sleep(max(wait_time, 0))
                timestamps.append(time.monotonic())
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls):
    """Ensure a class has only one instance (thread-safe)."""
    instances = {}
    lock = threading.Lock()

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


# --- Usage examples ---

@retry(times=3, delay=0.5, exceptions=(ConnectionError,))
def fetch_from_flaky_service(url):
    """Simulates an unreliable network call."""
    print(f"Fetching {url}...")
    raise ConnectionError("service unavailable")


@timer
def compute_heavy_task(n):
    return sum(i * i for i in range(n))


@rate_limit(calls=2, period=1.0)
def call_external_api(payload):
    print(f"Calling API with {payload}")


@singleton
class DatabaseConnection:
    def __init__(self):
        print("Establishing new database connection...")


if __name__ == "__main__":
    compute_heavy_task(1_000_000)

    for i in range(4):
        call_external_api(f"request-{i}")

    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print("Same instance:", db1 is db2)

    try:
        fetch_from_flaky_service("http://example.com")
    except ConnectionError as e:
        print(f"Final failure after retries: {e}")
