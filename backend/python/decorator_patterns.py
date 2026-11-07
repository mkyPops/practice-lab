"""
Practical decorator patterns: retry, timer, rate_limit, and singleton.
Each decorator is reusable and generic; usage examples are at the bottom.
"""

import time
import random
import functools
import threading


def retry(times=3, delay=1.0, backoff=2.0, exceptions=(Exception,)):
    """Retry a function call on failure, with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == times:
                        raise
                    print(f"[retry] {func.__name__} failed ({exc}); "
                          f"attempt {attempt}/{times}, retrying in {current_delay:.1f}s")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


def timer(func):
    """Measure and print the execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def rate_limit(calls=5, period=1.0):
    """Limit a function to `calls` invocations per `period` seconds (thread-safe)."""
    def decorator(func):
        lock = threading.Lock()
        timestamps = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.monotonic()
                # drop timestamps older than the window
                while timestamps and now - timestamps[0] > period:
                    timestamps.pop(0)
                if len(timestamps) >= calls:
                    wait = period - (now - timestamps[0])
                    time.sleep(max(wait, 0))
                timestamps.append(time.monotonic())
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls):
    """Ensure only one instance of a class is ever created (thread-safe)."""
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

@retry(times=4, delay=0.3, exceptions=(ConnectionError,))
def flaky_network_call():
    if random.random() < 0.7:
        raise ConnectionError("simulated network failure")
    return "network response OK"


@timer
def compute_sum(n):
    return sum(range(n))


@rate_limit(calls=3, period=1.0)
def call_external_api(i):
    print(f"[api] request #{i} sent at {time.strftime('%X')}")


@singleton
class ConfigManager:
    def __init__(self):
        self.settings = {"env": "production"}


if __name__ == "__main__":
    print(flaky_network_call())
    print(compute_sum(1_000_000))

    for i in range(6):
        call_external_api(i)

    cfg1 = ConfigManager()
    cfg2 = ConfigManager()
    print("Same instance:", cfg1 is cfg2)
