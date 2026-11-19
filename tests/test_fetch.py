import httpx
import pytest

from app import fetch
from app.fetch import FetchError, fetch_posts, parse_posts

GOOD = {"userId": 1, "id": 1, "title": "t", "body": "b"}


def make_response(status: int, data: list | None = None) -> httpx.Response:
    request = httpx.Request("GET", "https://example.com/posts")
    return httpx.Response(status, json=data or [], request=request)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Make retries instant in tests."""
    monkeypatch.setattr(fetch.time, "sleep", lambda seconds: None)


def fake_api(monkeypatch, responses: list):
    """Make httpx.get return these responses, one per call."""
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        item = responses[len(calls) - 1]
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(httpx, "get", fake_get)
    return calls


def test_success_returns_validated_posts(monkeypatch):
    calls = fake_api(monkeypatch, [make_response(200, [GOOD])])
    posts = fetch_posts("https://example.com")
    assert calls == ["https://example.com/posts"]
    assert posts[0].user_id == 1


def test_invalid_post_is_skipped():
    bad = {"userId": 1, "id": "abc", "title": "t", "body": "b"}
    posts = parse_posts([GOOD, bad])
    assert len(posts) == 1


def test_retries_on_503_then_succeeds(monkeypatch):
    calls = fake_api(monkeypatch, [make_response(503), make_response(200, [GOOD])])
    posts = fetch_posts("https://example.com")
    assert len(calls) == 2
    assert len(posts) == 1


def test_retries_on_timeout_then_succeeds(monkeypatch):
    timeout = httpx.ReadTimeout("too slow")
    calls = fake_api(monkeypatch, [timeout, make_response(200, [GOOD])])
    fetch_posts("https://example.com")
    assert len(calls) == 2


def test_no_retry_on_404(monkeypatch):
    calls = fake_api(monkeypatch, [make_response(404)])
    with pytest.raises(FetchError):
        fetch_posts("https://example.com")
    assert len(calls) == 1


def test_gives_up_after_max_retries(monkeypatch):
    calls = fake_api(monkeypatch, [make_response(503)] * 3)
    with pytest.raises(FetchError):
        fetch_posts("https://example.com", max_retries=3)
    assert len(calls) == 3
