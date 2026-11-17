from app.db import connect, count_posts, save_posts

FAKE_POSTS = [
    {"userId": 1, "id": 1, "title": "a", "body": "x"},
    {"userId": 1, "id": 2, "title": "b", "body": "y"},
]


def test_save_and_count(tmp_path):
    conn = connect(tmp_path / "test.db")
    written = save_posts(conn, FAKE_POSTS)
    assert written == 2
    assert count_posts(conn) == 2


def test_rerun_does_not_duplicate(tmp_path):
    conn = connect(tmp_path / "test.db")
    save_posts(conn, FAKE_POSTS)
    save_posts(conn, FAKE_POSTS)
    assert count_posts(conn) == 2
