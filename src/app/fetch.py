import logging
import time

import httpx
from pydantic import ValidationError

from app.models import Post

logger = logging.getLogger(__name__)  # this file's diary

BASE_URL = "https://jsonplaceholder.typicode.com"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class FetchError(Exception):
    """Raised when posts cannot be fetched."""


def parse_posts(raw: list[dict]) -> list[Post]:
    """Check each item. Keep good ones, skip and log bad ones."""
    posts = []
    for item in raw:
        try:
            posts.append(Post.model_validate(item))  # guard checks it
        except ValidationError as exc:  # guard said no
            logger.warning("Skipping invalid post %s: %s", item.get("id"), exc.errors()[0]["msg"])
    return posts


def fetch_posts(
    base_url: str = BASE_URL,
    timeout: float = 10.0,
    max_retries: int = 3,
    backoff: float = 1.0,
) -> list[Post]:
    """Return checked posts. Retry on timeouts, 429 and 5xx."""
    url = f"{base_url}/posts"
    for attempt in range(1, max_retries + 1):  # attempt = 1, 2, 3
        try:
            response = httpx.get(url, timeout=timeout)
            response.raise_for_status()
            return parse_posts(response.json())  # success: leave right away
        except httpx.HTTPStatusError as exc:  # server answered with an error code
            status = exc.response.status_code
            if status not in RETRYABLE_STATUS:  # wrong number: stop now
                raise FetchError(f"Request failed with status {status}") from exc
            logger.warning("Attempt %d/%d got status %d", attempt, max_retries, status)
        except httpx.TransportError as exc:  # no answer at all: timeout, no internet
            logger.warning("Attempt %d/%d failed: %s", attempt, max_retries, exc)

        if attempt < max_retries:  # don't wait after the last try
            wait = backoff * 2 ** (attempt - 1)  # 1s, 2s, 4s...
            logger.info("Retrying in %.1fs", wait)
            time.sleep(wait)

    raise FetchError(f"Gave up after {max_retries} attempts")  # all tries failed
