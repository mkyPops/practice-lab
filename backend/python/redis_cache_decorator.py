"""
Redis caching decorator.

Provides `redis_cache`, a decorator factory that caches the return value of
a function in Redis. Cache keys are derived by hashing the function's
qualified name together with its call arguments, and entries expire after
a configurable TTL (time-to-live).
"""

import functools
import hashlib
import pickle

import redis

# Single shared Redis connection used by all decorated functions.
_redis_client = redis.Redis(host="localhost", port=6379, db=0)


def _make_cache_key(prefix, args, kwargs):
    """Build a deterministic, hashed cache key from call arguments."""
    # repr() gives a stable textual form for most common argument types.
    raw_key = pickle.dumps((args, sorted(kwargs.items())))
    digest = hashlib.sha256(raw_key).hexdigest()
    return f"{prefix}:{digest}"


def redis_cache(ttl=300, client=None):
    """
    Decorator that caches a function's result in Redis.

    Args:
        ttl: Time-to-live for cache entries, in seconds.
        client: Optional redis.Redis instance (defaults to module client),
            useful for testing or custom connection settings.
    """
    def decorator(func):
        cache_prefix = f"{func.__module__}.{func.__qualname__}"
        redis_conn = client or _redis_client

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = _make_cache_key(cache_prefix, args, kwargs)

            cached = redis_conn.get(cache_key)
            if cached is not None:
                try:
                    return pickle.loads(cached)
                except (pickle.PickleError, EOFError):
                    # Corrupted cache entry; fall through and recompute.
                    pass

            result = func(*args, **kwargs)

            try:
                redis_conn.setex(cache_key, ttl, pickle.dumps(result))
            except redis.RedisError:
                # Caching failure shouldn't break the caller's logic.
                pass

            return result

        # Allow manual cache invalidation for a specific call.
        def invalidate(*args, **kwargs):
            cache_key = _make_cache_key(cache_prefix, args, kwargs)
            redis_conn.delete(cache_key)

        wrapper.invalidate = invalidate
        return wrapper

    return decorator


if __name__ == "__main__":
    @redis_cache(ttl=60)
    def slow_square(n):
        print(f"Computing square of {n}...")
        return n * n

    print(slow_square(4))
    print(slow_square(4))  # served from cache, no "Computing" print
    slow_square.invalidate(4)
    print(slow_square(4))  # recomputes after invalidation
