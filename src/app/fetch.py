# 1. Go to the URL and ask for posts
# 2. Don't wait forever
# 3. If the server says error, stop
# 4. Turn the reply into Python data
import httpx

BASE_URL = "https://jsonplaceholder.typicode.com"


def fetch_posts(base_url: str = BASE_URL, timeout: float = 10.0) -> list[dict]:
    """Return all posts from the API as a list of dicts."""
    # 1. Go to the URL and ask for posts + 2. Don't wait forever
    response = httpx.get(f"{base_url}/posts", timeout=timeout)
    # 3. If the server says error, stop
    response.raise_for_status()
    # 4. Turn the reply into Python data
    return response.json()
