import httpx

from app import fetch


class FakeResponse:
    def raise_for_status(self) -> None:
        pass

    def json(self) -> list[dict]:
        return [{"userId": 1, "id": 1, "title": "t", "body": "b"}]


def test_fetch_posts_calls_the_right_url(monkeypatch):
    calls = {}

    def fake_get(url, timeout):
        calls["url"] = url
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)
    posts = fetch.fetch_posts("https://example.com")

    assert calls["url"] == "https://example.com/posts"
    assert posts[0]["id"] == 1
