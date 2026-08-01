"""
Celery task demonstrating automatic retries with exponential backoff.

Simulates calling an unreliable external service (e.g. a flaky HTTP API).
Transient errors are retried with exponentially increasing delay, jitter,
and a hard cap on both delay and number of attempts.
"""

import random
import logging

import requests
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

logger = get_task_logger(__name__)

# Exceptions considered transient and worth retrying.
TRANSIENT_ERRORS = (requests.ConnectionError, requests.Timeout)

MAX_RETRIES = 5
BASE_DELAY = 2  # seconds
MAX_DELAY = 60  # seconds


@app.task(bind=True, max_retries=MAX_RETRIES)
def fetch_resource(self, url: str) -> dict:
    """Fetch a URL, retrying transient network failures with backoff."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except TRANSIENT_ERRORS as exc:
        # Exponential backoff with jitter, capped at MAX_DELAY.
        delay = min(BASE_DELAY * (2 ** self.request.retries), MAX_DELAY)
        jitter = random.uniform(0, delay * 0.1)
        countdown = delay + jitter

        logger.warning(
            "Transient error fetching %s (attempt %d/%d): %s. "
            "Retrying in %.1fs",
            url,
            self.request.retries + 1,
            MAX_RETRIES,
            exc,
            countdown,
        )
        raise self.retry(exc=exc, countdown=countdown)
    except requests.HTTPError as exc:
        # Non-transient HTTP errors (4xx/5xx) are not retried.
        logger.error("Non-retryable HTTP error fetching %s: %s", url, exc)
        raise
