import logging
import os
import sys

from dotenv import load_dotenv

from app.db import connect, count_posts, save_posts
from app.fetch import BASE_URL, FetchError, fetch_posts

logger = logging.getLogger(__name__)


def run() -> None:
    # 1. Set up the diary: show INFO and above, with time, level and file name
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    load_dotenv()
    base_url = os.getenv("API_BASE_URL", BASE_URL)
    db_path = os.getenv("DB_PATH", "data.db")

    # 2. Catch our own alarm and stop politely
    try:
        posts = fetch_posts(base_url)
    except FetchError as exc:
        logger.error("Could not fetch posts: %s", exc)
        sys.exit(1)

    conn = connect(db_path)
    written = save_posts(conn, posts)
    # 3. print -> logger.info
    logger.info("Saved %d posts. Table now has %d rows.", written, count_posts(conn))
    conn.close()


if __name__ == "__main__":
    run()
