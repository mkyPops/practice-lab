"""
A small HTTP client wrapper around `requests` that automatically retries
failed requests using exponential backoff with jitter. Retries are
triggered by connection errors, timeouts, and configurable HTTP status
codes (e.g. 429, 5xx).
"""

import random
import time
import logging

import requests

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(
        self,
        base_url="",
        max_retries=5,
        backoff_base=0.5,
        backoff_max=30.0,
        retry_statuses=frozenset({429, 500, 502, 503, 504}),
        timeout=10,
        session=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.retry_statuses = retry_statuses
        self.timeout = timeout
        self.session = session or requests.Session()

    def request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}" if self.base_url else path
        kwargs.setdefault("timeout", self.timeout)
        attempt = 0

        while True:
            try:
                response = self.session.request(method, url, **kwargs)
            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt >= self.max_retries:
                    raise
                self._sleep(attempt, reason=str(exc))
                attempt += 1
                continue

            if response.status_code in self.retry_statuses and attempt < self.max_retries:
                self._sleep(attempt, reason=f"status {response.status_code}")
                attempt += 1
                continue

            # Either success, or a non-retryable failure / exhausted retries.
            return response

    def _sleep(self, attempt, reason):
        # Exponential backoff capped at backoff_max, with full jitter.
        delay = min(self.backoff_base * (2 ** attempt), self.backoff_max)
        delay = random.uniform(0, delay)
        logger.warning(
            "Retrying request (attempt %d/%d) after %.2fs due to: %s",
            attempt + 1, self.max_retries, delay, reason,
        )
        time.sleep(delay)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
