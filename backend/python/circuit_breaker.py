"""
Circuit breaker decorator: wraps a callable and stops invoking it after
too many consecutive failures, "opening" the circuit for a cooldown
period. After the cooldown, a single trial call is allowed (half-open
state) to test if the dependency has recovered.
"""

import functools
import threading
import time


class CircuitBreakerOpenError(Exception):
    """Raised when calls are blocked because the circuit is open."""


def circuit_breaker(failure_threshold=5, recovery_timeout=30.0, expected_exception=Exception):
    """
    Decorator implementing the circuit breaker pattern.

    :param failure_threshold: consecutive failures before opening the circuit.
    :param recovery_timeout: seconds to wait before allowing a trial call.
    :param expected_exception: exception type(s) that count as failures.
    """
    def decorator(func):
        state = {"failures": 0, "opened_at": None, "status": "closed"}
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                if state["status"] == "open":
                    elapsed = time.monotonic() - state["opened_at"]
                    if elapsed < recovery_timeout:
                        raise CircuitBreakerOpenError(
                            f"Circuit for '{func.__name__}' is open; "
                            f"retry in {recovery_timeout - elapsed:.1f}s"
                        )
                    # Cooldown elapsed: allow one trial call (half-open).
                    state["status"] = "half-open"

            try:
                result = func(*args, **kwargs)
            except expected_exception:
                with lock:
                    state["failures"] += 1
                    # Any failure while half-open re-opens the circuit immediately.
                    if state["status"] == "half-open" or state["failures"] >= failure_threshold:
                        state["status"] = "open"
                        state["opened_at"] = time.monotonic()
                raise
            else:
                with lock:
                    # Success resets the breaker fully, whether closed or half-open.
                    state["failures"] = 0
                    state["status"] = "closed"
                    state["opened_at"] = None
                return result

        def reset():
            """Manually reset the circuit breaker to closed state."""
            with lock:
                state["failures"] = 0
                state["status"] = "closed"
                state["opened_at"] = None

        wrapper.reset = reset
        wrapper.state = state
        return wrapper

    return decorator


if __name__ == "__main__":
    # Simple demonstration of the circuit breaker in action.
    attempt_counter = {"count": 0}

    @circuit_breaker(failure_threshold=3, recovery_timeout=2.0, expected_exception=RuntimeError)
    def flaky_service():
        attempt_counter["count"] += 1
        if attempt_counter["count"] <= 4:
            raise RuntimeError("service unavailable")
        return "success"

    for i in range(6):
        try:
            print(f"Call {i}: {flaky_service()}")
        except (RuntimeError, CircuitBreakerOpenError) as exc:
            print(f"Call {i}: failed -> {exc}")
        time.sleep(0.5)
