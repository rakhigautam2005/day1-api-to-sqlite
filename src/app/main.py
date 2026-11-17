# 1. Load settings from .env
# 2. Get posts from the API
# 3. Open the database
# 4. Save the posts
# 5. Report what happened
import os

from dotenv import load_dotenv

from app.db import connect, count_posts, save_posts
from app.fetch import BASE_URL, fetch_posts


def run() -> None:
    # 1. Load settings from .env
    load_dotenv()
    base_url = os.getenv("API_BASE_URL", BASE_URL)
    db_path = os.getenv("DB_PATH", "data.db")

    # 2. Get posts from the API
    posts = fetch_posts(base_url)

    # 3. Open the database
    conn = connect(db_path)

    # 4. Save the posts
    written = save_posts(conn, posts)

    # 5. Report what happened
    print(f"Saved {written} posts. Table now has {count_posts(conn)} rows.")
    conn.close()


if __name__ == "__main__":
    run()
