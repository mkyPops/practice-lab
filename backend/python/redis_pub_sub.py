"""
Redis pub/sub message broker.

Provides a Publisher and Subscriber built on a shared redis.ConnectionPool,
with automatic reconnection and exponential backoff when the connection
to Redis drops (e.g. network blip, Redis restart).
"""

import time
import logging

import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("redis_broker")

# Shared pool so publisher/subscribers reuse TCP connections efficiently.
POOL = redis.ConnectionPool(
    host="localhost", port=6379, db=0, max_connections=20, decode_responses=True
)


class Publisher:
    def __init__(self, pool: redis.ConnectionPool = POOL):
        self.client = redis.Redis(connection_pool=pool)

    def publish(self, channel: str, message: str, retries: int = 3) -> bool:
        """Publish a message, retrying on connection errors."""
        for attempt in range(1, retries + 1):
            try:
                self.client.publish(channel, message)
                return True
            except (redis.ConnectionError, redis.TimeoutError) as exc:
                logger.warning("Publish attempt %d failed: %s", attempt, exc)
                time.sleep(min(2 ** attempt, 10))
        logger.error("Giving up publishing to %s after %d attempts", channel, retries)
        return False


class Subscriber:
    def __init__(self, channel: str, pool: redis.ConnectionPool = POOL):
        self.channel = channel
        self.pool = pool
        self.client = redis.Redis(connection_pool=pool)
        self.pubsub = None
        self._connect()

    def _connect(self):
        """(Re)establish the pub/sub connection and subscription."""
        self.pubsub = self.client.pubsub()
        self.pubsub.subscribe(self.channel)
        logger.info("Subscribed to channel '%s'", self.channel)

    def listen(self, handler):
        """
        Block forever, invoking handler(message) for each real message.
        Automatically reconnects with backoff on dropped connections.
        """
        backoff = 1
        while True:
            try:
                for message in self.pubsub.listen():
                    if message["type"] != "message":
                        continue
                    backoff = 1  # reset backoff after a successful receive
                    handler(message["data"])
            except (redis.ConnectionError, redis.TimeoutError) as exc:
                logger.warning("Subscriber connection lost: %s", exc)
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
                try:
                    self._connect()
                except (redis.ConnectionError, redis.TimeoutError) as exc:
                    logger.warning("Reconnect failed: %s", exc)


if __name__ == "__main__":
    import threading

    def on_message(data):
        print(f"Received: {data}")

    sub = Subscriber("notifications")
    threading.Thread(target=sub.listen, args=(on_message,), daemon=True).start()

    pub = Publisher()
    time.sleep(1)  # give the subscriber a moment to attach
    pub.publish("notifications", "hello world")
    time.sleep(1)
